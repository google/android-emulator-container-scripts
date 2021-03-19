# Copyright 2021 The Android Open Source Project
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
import collections
import logging
import os
import shutil
import zipfile

from tqdm import tqdm

from emu.utils import api_codename


class AndroidReleaseZip(object):
    """Provides information of released android products.

    Every released zip file contains a source.properties file, this
    source.properties file contains [key]=[value] pairs with information
    about the contents of the zip.
    """

    def __init__(self, file_name):
        self.file_name = file_name
        if not zipfile.is_zipfile(file_name):
            raise Exception("{} is not a zipfile!".format(file_name))
        with zipfile.ZipFile(file_name, "r") as zip_file:
            self.props = collections.defaultdict(set)
            files = [x for x in zip_file.infolist() if "source.properties" in x.filename or "build.prop" in x.filename]
            for file in files:
                for key, value in self._unpack_properties(zip_file, file).items():
                    self.props[key] = value

    def _unpack_properties(self, zip_file, zip_info):
        prop = zip_file.read(zip_info).decode("utf-8").splitlines()
        res = dict([a.split("=") for a in prop if "=" in a])
        return res

    def __str__(self):
        return "{}-{}".format(self.description(), self.revision())

    def description(self):
        """Descripton of this release."""
        return self.props.get("Pkg.Desc")

    def revision(self):
        """The revision of this release."""
        return self.props.get("Pkg.Revision")

    def build_id(self):
        """The Pkg.BuildId or revision if build id is not available."""
        if "Pkg.BuildId" in self.props:
            return self.props.get("Pkg.BuildId")
        return self.revision()

    def is_system_image(self):
        """True if this zip file contains a system image."""
        return "System Image" in self.description() or "Android SDK Platform" in self.description()

    def is_emulator(self):
        """True if this zip file contains the android emulator."""
        return "Android Emulator" in self.description()

    def copy(self, destination):
        """Copy the zipfile to the given destination.

        If the destination is the same as this zipfile the current path
        will be returned a no copy is made.

        Args:
            destination ({string}): The destination to copy this zip to.

        Returns:
            {string}: The path where this zip file was copied to
        """
        try:
            return shutil.copy2(self.file_name, destination)
        except shutil.SameFileError:
            logging.warning("Will not copy to itself, ignoring..")
            return self.file_name

    def extract(self, destination):
        """Extract this release zip to the given destination

        Args:
            destination ({string}): The destination to extract the zipfile to.
        """

        zip_file = zipfile.ZipFile(self.file_name)
        print("Extracting: {} -> {}".format(self.file_name, destination))
        for info in tqdm(iterable=zip_file.infolist(), total=len(zip_file.infolist())):
            filename = zip_file.extract(info, path=destination)
            mode = info.external_attr >> 16
            if mode:
                os.chmod(filename, mode)


class SystemImageReleaseZip(AndroidReleaseZip):
    """An Android Release Zipfile containing an emulator system image."""

    ABI_CPU_MAP = {"armeabi-v7a": "arm", "arm64-v8a": "arm64", "x86_64": "x86_64", "x86": "x86"}
    SHORT_MAP = {"armeabi-v7a": "a32", "arm64-v8a": "a64", "x86_64": "x64", "x86": "x86"}
    SHORT_TAG = {
        "android": "aosp",
        "google_apis": "google",
        "google_apis_playstore": "playstore",
        "google_ndk_playstore": "ndk_playstore",
        "android-tv": "tv",
    }

    def __init__(self, file_name):
        super().__init__(file_name)
        if not self.is_system_image():
            raise Exception("{} is not a zip file with a system image".format(file_name))

        self.props["qemu.cpu"] = self.qemu_cpu()
        self.props["qemu.tag"] = self.tag()
        self.props["qemu.short_tag"] = self.short_tag()
        self.props["qemu.short_abi"] = self.short_abi()

    def api(self):
        """The api level, if any."""
        return self.props.get("AndroidVersion.ApiLevel", "")

    def codename(self):
        """First letter of the desert, if any."""
        if "AndroidVersion.CodeName" in self.props:
            return self.props["AndroidVersion.CodeName"]
        return api_codename(self.api())

    def abi(self):
        """The abi if any."""
        return self.props.get("SystemImage.Abi", "")

    def short_abi(self):
        """Shortened version of the ABI string."""
        if self.abi() not in self.SHORT_MAP:
            logging.error("%s not in short map", self)
        return self.SHORT_MAP[self.abi()]

    def qemu_cpu(self):
        """Returns the cpu architecture, derived from the abi."""
        return self.ABI_CPU_MAP.get(self.abi(), "None")

    def gpu(self):
        """Returns whether or not the system has gpu support."""
        return self.props.get("SystemImage.GpuSupport")

    def tag(self):
        """The tag associated with this release."""
        tag = self.props.get("SystemImage.TagId", "")
        if tag == "default" or tag.strip() == "":
            tag = "android"
        return tag

    def short_tag(self):
        """A shorthand tag."""
        return self.SHORT_TAG[self.tag()]
