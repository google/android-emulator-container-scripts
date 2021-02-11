# Copyright 2019 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import datetime
import logging
import os
import re
import shutil
import socket
import sys
import zipfile

import docker
from jinja2 import Environment, PackageLoader
from packaging import version
from tqdm import tqdm

import emu
from emu.android_release_zip import AndroidReleaseZip
from emu.platform_tools import PlatformTools
from emu.template_writer import TemplateWriter
from emu.utils import mkdir_p

METRICS_MESSAGE = """
By using this docker container you authorize Google to collect usage data for the Android Emulator
— such as how you utilize its features and resources, and how you use it to test applications.
This data helps improve the Android Emulator and is collected in accordance with
[Google's Privacy Policy](http://www.google.com/policies/privacy/)
"""
NO_METRICS_MESSAGE = "No metrics are collected when running this container."


class ProgressTracker(object):
    """Tracks progress using tqdm for a set of layers that are pushed."""

    def __init__(self):
        # This tracks the information for a given layer id.
        self.progress = {}
        self.idx = -1

    def __del__(self):
        for k in self.progress:
            self.progress[k]["tqdm"].close()

    def update(self, entry):
        """Update the progress bars given a an entry.."""
        if "id" not in entry:
            return

        identity = entry["id"]
        if identity not in self.progress:
            self.idx += 1
            self.progress[identity] = {
                "tqdm": tqdm(total=0, position=self.idx, unit="B", unit_scale=True),  # The progress bar
                "total": 0,  # Total of bytes we are shipping
                "status": "",  # Status message.
                "current": 0,  # Current of total already send.
            }
        prog = self.progress[identity]

        total = int(entry.get("progressDetail", {}).get("total", -1))
        current = int(entry.get("progressDetail", {}).get("current", 0))
        if prog["total"] != total and total != -1:
            prog["total"] = total
            prog["tqdm"].reset(total=total)
        if prog["status"] != entry["status"]:
            prog["tqdm"].set_description("{0} {1}".format(entry.get("status"), identity))
        if current != 0:
            diff = current - prog["current"]
            prog["current"] = current
            prog["tqdm"].update(diff)


class BaseDockerObject(object):
    """A Docker Device is capable of creating and launching docker images.

    In order to successfully create and launch a docker image you must either
    run this as root, or have enabled sudoless docker.
    """

    TAG_REGEX = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9._-]*:?[a-zA-Z0-9._-]*")
    GPU_BASEIMG = (
        "FROM nvidia/opengl:1.0-glvnd-runtime-ubuntu18.04 AS emulator\n"
        + "ENV NVIDIA_DRIVER_CAPABILITIES ${NVIDIA_DRIVER_CAPABILITIES},display"
    )
    DEFAULT_BASE_IMG = "FROM debian:stretch-slim AS emulator"

    def __init__(self, repo=None):
        self.container = None
        self.identity = None
        if repo and repo[-1] != "/":
            repo += "/"
        self.repo = repo

    def get_client(self):
        return docker.from_env()

    def get_api_client(self):
        try:
            api_client = docker.APIClient()
            logging.info(api_client.version())
            return api_client
        except:
            logging.exception("Failed to create default client, trying domain socket.", exc_info=True)

        api_client = docker.APIClient(base_url="unix://var/run/docker.sock")
        logging.info(api_client.version())
        return api_client

    def push(self):
        image = self.full_name()
        print("Pushing docker image: {}.. be patient this can take a while!".format(self.full_name()))
        tracker = ProgressTracker()
        try:
            client = docker.from_env()
            result = client.images.push(image, self.full_name(), stream=True, decode=True)
            for entry in result:
                tracker.update(entry)
            self.docker_image().tag("{}{}:latest".format(self.repo, self.image_name()))
        except:
            logging.exception("Failed to push image.", exc_info=True)
            logging.warning("You can manually push the image as follows:")
            logging.warning("docker push {}".format(image))

    def launch(self, port_map):
        """Launches the container with the given sha, publishing abd on port, and grpc on port 8554

        Returns the container.
        """
        image_sha = "{}:{}".format(self.image_name(), self.docker_tag())
        client = docker.from_env()
        try:
            container = client.containers.run(
                image=image_sha,
                privileged=True,
                publish_all_ports=True,
                detach=True,
                ports=port_map,
            )
            self.container = container
            print("Launched {} (id:{})".format(container.name, container.id))
            print("docker logs -f {}".format(container.name))
            print("docker stop {}".format(container.name))
            return container
        except:
            logging.exception("Unable to run the %s", image_sha)
            print("Unable to start the container, try running it as:")
            print("./run.sh ", image_sha)

    def create_container(self, dest):
        """Creates the docker container, returning the sha of the container, or None in case of failure."""
        identity = None
        image_tag = self.full_name()
        print("docker build {} -t {}".format(dest, image_tag))
        try:
            api_client = self.get_api_client()
            logging.info("build(path=%s, tag=%s, rm=True, decode=True)", dest, image_tag)
            result = api_client.build(path=dest, tag=image_tag, rm=True, decode=True)
            for entry in result:
                if "stream" in entry:
                    sys.stdout.write(entry["stream"])
                if "aux" in entry and "ID" in entry["aux"]:
                    identity = entry["aux"]["ID"]
        except:
            logging.exception("Failed to create container.", exc_info=True)
            logging.warning("You can manually create the container as follows:")
            logging.warning("docker build {} -t {}".format(dest, image_tag))

        return identity

    def pull(self, image, tag):
        """Tries to retrieve the given image and tag.

        Return True if succeeded, False when failed.
        """
        client = self.get_api_client()
        try:
            tracker = ProgressTracker()
            result = client.pull(self.repo + image, tag)
            for entry in result:
                tracker.update(entry)
        except:
            logging.info("Failed to retrieve image, this is not uncommon.", exc_info=True)
            return False

        return True

    def full_name(self):
        if self.repo:
            return "{}{}:{}".format(self.repo, self.image_name(), self.docker_tag())
        return (self.image_name(), self.docker_tag())

    def latest_name(self):
        if self.repo:
            return "{}{}:{}".format(self.repo, self.image_name(), "latest")
        return (self.image_name(), "latest")


    def create_cloud_build_step(self, dest):
        return {
            "name": "gcr.io/cloud-builders/docker",
            "args": [
                "build",
                "-t",
                self.full_name(),
                "-t",
                self.latest_name(),
                os.path.basename(dest),
            ],
        }
