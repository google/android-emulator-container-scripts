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

from emu.android_release_zip import AndroidReleaseZip
from emu.platform_tools import PlatformTools
from emu.template_writer import TemplateWriter
from emu.generators.base_docker import BaseDockerObject
from emu.utils import mkdir_p
from emu.emu_downloads_menu import SysImgInfo


class SystemImageDockerFile(BaseDockerObject):
    def __init__(self, sort, repo="us-docker.pkg.dev/android-emulator-268719/images"):
        super().__init__(repo)
        self.sysimg = None
        self.sysimginfo = None

        if type(sort) == SysImgInfo:
            self.sysimginfo = sort
        else:
            self.sysimg = AndroidReleaseZip(sort)
            if not self.sysimg.is_system_image():
                raise Exception("{} is not a zip file with a system image".format(sysimg))
            assert "ro.build.version.incremental" in self.sysimg.props

    def _copy_adb_to(self, dest):
        """Find adb, or download it if needed."""
        logging.info("Retrieving platform-tools")
        tools = PlatformTools()
        tools.extract_adb(dest)

    def write(self, dest):
        # Make sure the destination directory is empty.
        if self.sysimg == None:
            self.sysimg = AndroidReleaseZip(self.sysimginfo.download())

        if os.path.exists(dest):
            shutil.rmtree(dest)
        mkdir_p(dest)

        writer = TemplateWriter(dest)
        self._copy_adb_to(dest)

        props = self.sysimg.props
        dest_zip = os.path.basename(self.sysimg.copy(dest))
        props['sysimg_zip'] = dest_zip
        writer.write_template(
            "Dockerfile.system_image",
            props,
            rename_as="Dockerfile",
        )

    def image_name(self):
        if self.sysimginfo:
           return self.sysimginfo.image_name()
        if self.sysimg:
            return "sys-{}-{}-{}".format(self.sysimg.api(), self.sysimg.tag(), self.sysimg.abi())

    def docker_image(self):
        client = self.get_client()
        for img in client.images.list():
            for tag in img.tags:
                if self.image_name() in tag:
                    return img
        return None

    def docker_tag(self):
        if self.sysimg:
            return self.sysimg.props["ro.build.version.incremental"]
        if self.available():
            return self.image_labels()["ro.build.version.incremental"]

        # Unknown, revert to latest.
        return "latest"

    def available(self):
        return self.docker_image() != None

    def image_labels(self):
        if self.docker_image():
            return self.docker_image().labels
        return self.sysimg.props

    def build(self, dest):
        self.write(dest)
        return self.create_container(dest)

    def can_pull(self):
        return self.pull(self.image_name(), "latest")
