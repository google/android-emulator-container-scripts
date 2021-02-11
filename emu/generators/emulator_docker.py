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
import os
import shutil
import socket
import logging

import emu
from emu.android_release_zip import AndroidReleaseZip
from emu.platform_tools import PlatformTools
from emu.template_writer import TemplateWriter
from emu.utils import api_codename, mkdir_p

METRICS_MESSAGE = """
By using this docker container you authorize Google to collect usage data for the Android Emulator
— such as how you utilize its features and resources, and how you use it to test applications.
This data helps improve the Android Emulator and is collected in accordance with
[Google's Privacy Policy](http://www.google.com/policies/privacy/)
"""
NO_METRICS_MESSAGE = "No metrics are collected when running this container."
import logging
import os
import shutil

from emu.android_release_zip import AndroidReleaseZip
from emu.platform_tools import PlatformTools
from emu.template_writer import TemplateWriter
from emu.generators.base_docker import BaseDockerObject
from emu.utils import mkdir_p
from emu.emu_downloads_menu import SysImgInfo


class EmulatorDockerFile(BaseDockerObject):
    def __init__(self, emulator, sysdocker, repo=None, metrics=False, extra=""):
        self.emulator = AndroidReleaseZip(emulator)

        if type(extra) is list:
            extra = " ".join(extra)

        cpu = sysdocker.image_labels()["ro.product.cpu.abi"]
        self.extra = self._logger_flags(cpu) + " " + extra

        metrics_msg = NO_METRICS_MESSAGE
        if metrics:
            self.extra += " -metrics-collection"
            metrics_msg = METRICS_MESSAGE

        self.props = sysdocker.image_labels()
        self.props["playstore"] = self.props["qemu.tag"] == "google_apis_playstore"
        self.props["metrics"] = metrics_msg
        self.props["emu_build_id"] = self.emulator.build_id()
        self.props["from_base_img"] = sysdocker.full_name()

        assert "ro.system.build.version.sdk" in self.props, self.props
        assert "qemu.tag" in self.props
        assert "ro.product.cpu.abi" in self.props

        super().__init__(repo)

    def _logger_flags(self, cpu):
        if "arm" in cpu:
            return "-logcat *:V -show-kernel"
        else:
            return "-shell-serial file:/tmp/android-unknown/kernel.log -logcat-output /tmp/android-unknown/logcat.log"

    def write(self, dest, extra=""):
        # Make sure the destination directory is empty.
        if os.path.exists(dest):
            shutil.rmtree(dest)
        mkdir_p(dest)

        writer = TemplateWriter(dest)
        writer.write_template("avd/Pixel2.ini", self.props)
        writer.write_template("avd/Pixel2.avd/config.ini", self.props)

        # Include a README.MD message.
        writer.write_template(
            "emulator.README.MD",
            self.props,
            rename_as="README.MD",
        )

        writer.write_template("launch-emulator.sh", {"extra": self.extra + extra, "version": emu.__version__})
        writer.write_template("default.pa", {})

        writer.write_template(
            "Dockerfile.emulator",
            self.props,
            rename_as="Dockerfile",
        )

        self.emulator.extract(os.path.join(dest, "emu"))

    def image_name(self):
        return "{}-{}-{}".format(
            self.props["ro.system.build.version.sdk"], self.props["qemu.tag"], self.props["ro.product.cpu.abi"]
        )

    def docker_tag(self):
        return self.props["emu_build_id"]

    def build(self, dest):
        self.write(dest)
        return self.create_container(dest)
