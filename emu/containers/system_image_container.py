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
import logging
import os
import shutil

from emu.android_release_zip import SystemImageReleaseZip
from emu.platform_tools import PlatformTools
from emu.template_writer import TemplateWriter
from emu.containers.docker_container import DockerContainer
from emu.emu_downloads_menu import SysImgInfo


class SystemImageContainer(DockerContainer):
    def __init__(self, sort, repo="us-docker.pkg.dev/android-emulator-268719/images"):
        super().__init__(repo)
        self.system_image_zip = None
        self.system_image_info = None

        if type(sort) == SysImgInfo:
            self.system_image_info = sort
        else:
            self.system_image_zip = SystemImageReleaseZip(sort)
            assert "ro.build.version.incremental" in self.system_image_zip.props

    def _copy_adb_to(self, dest):
        """Find adb, or download it if needed."""
        logging.info("Retrieving platform-tools")
        tools = PlatformTools()
        tools.extract_adb(dest)

    def write(self, dest):
        # We do not really want to overwrite if the files already exist.
        # Make sure the destination directory is empty.
        if self.system_image_zip is None:
            self.system_image_zip = SystemImageReleaseZip(self.system_image_info.download(dest))

        writer = TemplateWriter(dest)
        self._copy_adb_to(dest)

        props = self.system_image_zip.props
        dest_zip = os.path.basename(self.system_image_zip.copy(dest))
        props["system_image_zip"] = dest_zip
        writer.write_template(
            "Dockerfile.system_image",
            props,
            rename_as="Dockerfile",
        )

    def image_name(self):
        if self.system_image_info:
            return self.system_image_info.image_name()
        if self.system_image_zip:
            return "sys-{}-{}-{}".format(
                self.system_image_zip.api(), self.system_image_zip.short_tag(), self.system_image_zip.short_abi()
            )

    def docker_tag(self):
        if self.system_image_zip:
            return self.system_image_zip.props["ro.build.version.incremental"]
        if super().available():
            return self.image_labels()["ro.build.version.incremental"]

        # Unknown, revert to latest.
        return "latest"

    def image_labels(self):
        if self.docker_image():
            return self.docker_image().labels
        return self.system_image_zip.props

    def depends_on(self):
        return "-"
