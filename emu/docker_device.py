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
import errno
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
from emu.emu_downloads_menu import AndroidReleaseZip, PlatformTools
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


def extract_zip(fname, path):
    zip_file = zipfile.ZipFile(fname)
    print("Extracting: {} -> {}".format(fname, path))
    for info in tqdm(iterable=zip_file.infolist(), total=len(zip_file.infolist())):
        filename = zip_file.extract(info, path=path)
        mode = info.external_attr >> 16
        if mode:
            os.chmod(filename, mode)


class DockerDevice(object):
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

    def __init__(self, emulator, sysimg, dest_dir, gpu=False, repo="", tag="", name=""):

        self.sysimg = AndroidReleaseZip(sysimg)
        self.emulator = AndroidReleaseZip(emulator)
        self.dest = dest_dir
        self.writer = TemplateWriter(dest_dir)
        if repo and repo[-1] != "/":
            repo += "/"
        if not name:
            name = self.sysimg.repo_friendly_name()
        repo += name
        if gpu:
            repo += "-gpu"
        if not tag:
            tag = self.emulator.build_id()

        self.tag = "{}:{}".format(repo, tag)
        if not self.TAG_REGEX.match(self.tag):
            raise Exception("The resulting tag: {} is not a valid docker tag.", self.tag)

        # The following are only set after creating/launching.
        self.container = None
        self.identity = None
        self.base_img = DockerDevice.DEFAULT_BASE_IMG
        if gpu:
            self.base_img = DockerDevice.GPU_BASEIMG

    def push(self, sha, latest=False):
        repo, tag = self.tag.rsplit(":")
        print("Pushing docker image: {}.. be patient this can take a while!".format(self.tag))
        tracker = ProgressTracker()
        try:
            client = docker.from_env()
            result = client.images.push(repo, tag, stream=True, decode=True)
            for entry in result:
                tracker.update(entry)
        except:
            logging.exception("Failed to push image.", exc_info=True)
            logging.warning("You can manually push the image as follows:")
            logging.warning("docker push {}".format(self.tag))

    def _copy_adb_to(self, dest):
        """Find adb, or download it if needed."""
        logging.info("Retrieving platform-tools")
        tools = PlatformTools()
        tools.extract_adb(dest)

    def _read_adb_key(self):
        adb_path = os.path.expanduser("~/.android/adbkey")
        if os.path.exists(adb_path):
            with open(adb_path, "r") as adb:
                return adb.read()
        return ""

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

    def create_container(self):
        """Creates the docker container, returning the sha of the container, or None in case of failure."""
        identity = None
        print("Creating docker image: {}.. be patient this can take a while!".format(self.tag))
        try:
            logging.info("build(path=%s, tag=%s, rm=True, decode=True)", self.dest, self.tag)
            api_client = self.get_api_client()
            result = api_client.build(path=self.dest, tag=self.tag, rm=True, decode=True)
            for entry in result:
                if "stream" in entry:
                    sys.stdout.write(entry["stream"])
                if "aux" in entry and "ID" in entry["aux"]:
                    identity = entry["aux"]["ID"]
        except:
            logging.exception("Failed to create container.", exc_info=True)
            logging.warning("You can manually create the container as follows:")
            logging.warning("docker build {}".format(self.dest))

        self.identity = identity
        return identity

    def create_cloud_build_step(self):
        return {"name": "gcr.io/cloud-builders/docker", "args": ["build", "-t", self.tag, os.path.basename(self.dest)]}

    def launch(self, image_sha, port=5555):
        """Launches the container with the given sha, publishing abd on port, and grpc on port 8554

           Returns the container.
        """
        client = docker.from_env()
        try:
            container = client.containers.run(
                image=image_sha,
                privileged=True,
                publish_all_ports=True,
                detach=True,
                ports={"5555/tcp": port, "8554/tcp": 8554},
                environment={"ADBKEY": self._read_adb_key()},
            )
            self.container = container
            print("Launched {} (id:{})".format(container.name, container.id))
            print("docker logs -f {}".format(container.name))
            print("docker stop {}".format(container.name))
            return container
        except:
            logging.exception("Unable to run the %s", image_sha)
            print("Unable to start the container, try running it as:")
            print("./run.sh {}", image_sha)

    def bin_place_emulator_files(self, by_copying_zip_files):
        """Bin places the emulator files for the docker file."""
        if by_copying_zip_files:
            logging.info("Copying zips to docker src dir: %s", self.dest)
            shutil.copy2(self.emulator.fname, self.dest)
            shutil.copy2(self.sysimg.fname, self.dest)
            logging.info("Done copying")
        else:
            logging.info("Unzipping zips to docker src dir: %s", self.dest)
            extract_zip(self.emulator.fname, os.path.join(self.dest, "emu"))
            extract_zip(self.sysimg.fname, os.path.join(self.dest, "sys"))
            logging.info("Done unzipping")

    def create_docker_file(self, extra="", metrics=False, by_copying_zip_files=False):
        logging.info("Emulator zip: %s", self.emulator)
        logging.info("Sysimg zip: %s", self.sysimg)
        logging.info("Docker src dir: %s", self.dest)

        date = datetime.datetime.utcnow().isoformat("T") + "Z"

        # Make sure the destination directory is empty.
        if os.path.exists(self.dest):
            shutil.rmtree(self.dest)
        mkdir_p(self.dest)

        self.bin_place_emulator_files(by_copying_zip_files)
        self._copy_adb_to(self.dest)
        self.writer.write_template("avd/Pixel2.ini", {"api": self.sysimg.api()})
        self.writer.write_template(
            "avd/Pixel2.avd/config.ini",
            {
                "playstore": self.sysimg.tag() == "google_apis_playstore",
                "abi": self.sysimg.abi(),
                "cpu": self.sysimg.cpu(),
                "tag": self.sysimg.tag(),
            },
        )

        metrics_msg = NO_METRICS_MESSAGE
        # Only version 29.3.1 >= can collect metrics.
        if metrics and version.parse(self.emulator.revision()) >= version.parse("29.3.1"):
            extra += " -metrics-collection"
            metrics_msg = METRICS_MESSAGE

        # Include a README.MD message.
        self.writer.write_template(
            "emulator.README.MD",
            {
                "metrics": metrics_msg,
                "dessert": self.sysimg.codename(),
                "tag": self.sysimg.tag(),
                "container_id": self.tag,
                "emu_build_id": self.emulator.build_id(),
            },
            rename_as="README.MD",
        )

        extra += " {}".format(self.sysimg.logger_flags())
        self.writer.write_template("launch-emulator.sh", {"extra": extra, "version": emu.__version__})
        self.writer.write_template("default.pa", {})

        src_template = "Dockerfile.from_zip" if by_copying_zip_files else "Dockerfile"
        self.writer.write_template(
            src_template,
            {
                "user": "{}@{}".format(os.environ.get("USER", "unknown"), socket.gethostname()),
                "tag": self.sysimg.tag(),
                "api": self.sysimg.api(),
                "abi": self.sysimg.abi(),
                "cpu": self.sysimg.cpu(),
                "gpu": self.sysimg.gpu(),
                "emu_zip": os.path.basename(self.emulator.fname),
                "emu_build_id": self.emulator.build_id(),
                "sysimg_zip": os.path.basename(self.sysimg.fname),
                "date": date,
                "from_base_img": self.base_img,
            },
            rename_as="Dockerfile",
        )
