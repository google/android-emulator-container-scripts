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

import emu
from emu.android_release_zip import AndroidReleaseZip
from emu.containers.docker_container import DockerContainer
from emu.template_writer import TemplateWriter


class EmulatorContainer(DockerContainer):

    METRICS_MESSAGE = """
        By using this docker container you authorize Google to collect usage data for the Android Emulator
        — such as how you utilize its features and resources, and how you use it to test applications.
        This data helps improve the Android Emulator and is collected in accordance with
        [Google's Privacy Policy](http://www.google.com/policies/privacy/)
        """
    NO_METRICS_MESSAGE = "No metrics are collected when running this container."

    def __init__(self, emulator, system_image_container, repository=None, metrics=False, extra=""):
        self.emulator_zip = AndroidReleaseZip(emulator)
        self.system_image_container = system_image_container
        self.metrics = metrics

        if type(extra) is list:
            extra = " ".join(extra)

        cpu = system_image_container.image_labels()["ro.product.cpu.abi"]
        self.extra = self._logger_flags(cpu) + " " + extra

        metrics_msg = EmulatorContainer.NO_METRICS_MESSAGE
        if metrics:
            self.extra += " -metrics-collection"
            metrics_msg = EmulatorContainer.METRICS_MESSAGE

        self.props = system_image_container.image_labels()
        self.props["playstore"] = self.props["qemu.tag"] == "google_apis_playstore"
        self.props["metrics"] = metrics_msg
        self.props["emu_build_id"] = self.emulator_zip.build_id()
        self.props["from_base_img"] = system_image_container.full_name()

        for expect in [
            "ro.build.version.sdk",
            "qemu.tag",
            "qemu.short_tag",
            "qemu.short_abi",
            "ro.product.cpu.abi",
        ]:
            assert expect in self.props, "{} is not in {}".format(expect, self.props)

        super().__init__(repository)

    def _logger_flags(self, cpu):
        if "arm" in cpu:
            return "-logcat *:V -show-kernel"
        else:
            return "-shell-serial file:/tmp/android-unknown/kernel.log -logcat-output /tmp/android-unknown/logcat.log"

    def write(self, dest):
        # Make sure the destination directory is empty.
        self.clean(dest)

        writer = TemplateWriter(dest)
        writer.write_template("avd/Pixel2.ini", self.props)
        writer.write_template("avd/Pixel2.avd/config.ini", self.props)

        # Include a README.MD message.
        writer.write_template(
            "emulator.README.MD",
            self.props,
            rename_as="README.MD",
        )

        writer.write_template("launch-emulator.sh", {"extra": self.extra, "version": emu.__version__})
        writer.write_template("default.pa", {})

        writer.write_template(
            "Dockerfile.emulator",
            self.props,
            rename_as="Dockerfile",
        )

        self.emulator_zip.extract(os.path.join(dest, "emu"))

    def image_name(self):
        name = "{}-{}-{}".format(
            self.props["ro.build.version.sdk"], self.props["qemu.short_tag"], self.props["qemu.short_abi"]
        )
        if not self.metrics:
            return "{}-no-metrics".format(name)
        return name

    def docker_tag(self):
        return self.props["emu_build_id"]

    def depends_on(self):
        if not self.system_image_container.can_pull():
            return self.system_image_container.image_name()
        else:
            return "-"
