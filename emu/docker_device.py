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
import json
import logging
import re
import os
import shutil
import socket
import sys
from distutils.spawn import find_executable

import docker
from jinja2 import Environment, PackageLoader
from tqdm import tqdm

import emu
from emu.emu_downloads_menu import AndroidReleaseZip, PlatformTools


def mkdir_p(path):
    """Make directories recursively if path not exists."""
    if not os.path.exists(path):
        os.makedirs(path)


class DockerDevice(object):
    """A Docker Device is capable of creating and launching docker images.

    In order to successfully create and launch a docker image you must either
    run this as root, or have enabled sudoless docker.
    """

    TAG_REGEX = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9._-]*:?[a-zA-Z0-9._-]*")

    def __init__(self, emulator, sysimg, dest_dir, tag=""):

        self.sysimg = AndroidReleaseZip(sysimg)
        self.emulator = AndroidReleaseZip(emulator)
        self.dest = dest_dir
        self.env = Environment(loader=PackageLoader("emu", "templates"))
        if not tag:
            tag = "{}-{}-{}-{}-{}".format(
                self.sysimg.tag(), self.sysimg.api(), self.sysimg.codename(), self.sysimg.abi(), self.emulator.revision()
            )
        self.tag = tag.replace(" ", "_")
        self.tag = "aemu:{}".format(tag)
        if not self.TAG_REGEX.match(self.tag):
            raise Exception("The resulting tag: {} is not a valid docker tag.", self.tag)

        # The following are only set after creating/launching.
        self.container = None
        self.identity = None

    def _copy_adb_to(self, dest):
        """Find adb, or download it if needed."""
        adb_loc = None
        if "linux" in sys.platform:
            adb_loc = os.path.join(os.environ.get("ANDROID_SDK_ROOT", ""), "platform-tools", "adb")
            if not (os.path.exists(adb_loc) and os.access(adb_loc, os.X_OK)):
                adb_loc = find_executable("adb")

        if adb_loc is None:
            logging.info("No local adb, retrieving platform-tools")
            tools = PlatformTools()
            tools.extract_adb(dest)
        else:
            logging.info("Copying %s to %s", adb_loc, dest)
            shutil.copy2(adb_loc, dest)

    def _read_adb_key(self):
        adb_path = os.path.expanduser("~/.android/adbkey")
        if os.path.exists(adb_path):
            with open(adb_path, "r") as adb:
                return adb.read()
        return ""

    def _write_template(self, tmpl_file, template_dict):
        """Loads the the given template, writing it out to the dest_dir.

            Note: the template will be written {dest_dir}/{tmpl_file},
            directories will be created if the do not yet exist.
        """
        dest = os.path.join(self.dest, tmpl_file)
        dest_dir = os.path.dirname(dest)
        mkdir_p(dest_dir)
        logging.info("Writing: %s with %s", dest, template_dict)
        template = self.env.get_template(tmpl_file)
        with open(dest, "w") as dfile:
            dfile.write(template.render(template_dict))

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
            print("You can manually create the container as follows:")
            print("docker build {}".format(self.dest))

        self.identity = identity
        return identity

    def launch(self, image_sha, port=5555):
        """Launches the container with the given sha, publishing abd on port, and grpc on port + 1.

           Returns the container.
        """
        client = docker.from_env()
        try:
            container = client.containers.run(
                image=image_sha,
                privileged=True,
                publish_all_ports=True,
                detach=True,
                ports={"5555/tcp": port, "5556/tcp": port + 1},
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

    def create_docker_file(self, extra=""):
        logging.info("Emulator zip: %s", self.emulator)
        logging.info("Sysimg zip: %s", self.sysimg)
        logging.info("Docker src dir: %s", self.dest)

        date = datetime.datetime.utcnow().isoformat("T") + "Z"

        # Make sure the destination directory is empty.
        if os.path.exists(self.dest):
            shutil.rmtree(self.dest)
        mkdir_p(self.dest)

        logging.info("Copying zips to docker src dir: %s", self.dest)
        shutil.copy2(self.emulator.fname, self.dest)
        shutil.copy2(self.sysimg.fname, self.dest)
        logging.info("Done copying")

        self._copy_adb_to(self.dest)

        self._write_template("avd/Pixel2.ini", {"api": self.sysimg.api()})
        self._write_template(
            "avd/Pixel2.avd/config.ini",
            {
                "playstore": self.sysimg.tag() == "google_apis_playstore",
                "abi": self.sysimg.abi(),
                "cpu": self.sysimg.cpu(),
                "tag": self.sysimg.tag(),
            },
        )
        extra += " {}".format(self.sysimg.logger_flags())
        self._write_template("launch-emulator.sh", {"extra": extra, "version": emu.__version__})
        self._write_template("default.pa", {})
        self._write_template(
            "Dockerfile",
            {
                "user": "{}@{}".format(os.environ.get("USER", "unknown"), socket.gethostname()),
                "tag": self.sysimg.tag(),
                "api": self.sysimg.api(),
                "abi": self.sysimg.abi(),
                "cpu": self.sysimg.cpu(),
                "gpu": self.sysimg.gpu(),
                "emu_zip": os.path.basename(self.emulator.fname),
                "emu_build_id": self.emulator.revision(),
                "sysimg_zip": os.path.basename(self.sysimg.fname),
                "date": date,
            },
        )
