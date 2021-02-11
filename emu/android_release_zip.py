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
import logging
import os
import zipfile
import collections
from emu.utils import api_codename
import shutil

from tqdm import tqdm


class AndroidReleaseZip(object):
    """Provides information of released android products.

    Every released zip file contains a source.properties file, this
    source.properties file contains [key]=[value] pairs with information
    about the contents of the zip.
    """

    ABI_CPU_MAP = {"armeabi-v7a": "arm", "arm64-v8a": "arm64", "x86_64": "x86_64", "x86": "x86"}
    SHORT_MAP = {"armeabi-v7a": "a32", "arm64-v8a": "a64", "x86_64": "x64", "x86": "x86"}
    SHORT_TAG = {
        "android": "aosp",
        "google_apis": "google",
        "google_apis_playstore": "playstore",
        "google_ndk_playstore": "ndk_playstore",
        "android-tv" : "tv",
    }

    def __init__(self, fname):
        self.fname = fname
        if not zipfile.is_zipfile(fname):
            raise Exception("{} is not a zipfile!".format(fname))
        with zipfile.ZipFile(fname, "r") as sysimg:
            self.props = collections.defaultdict(set)
            files = [x for x in sysimg.infolist() if "source.properties" in x.filename or "build.prop" in x.filename]
            for fn in files:
                for k, v in self._unpack_properties(sysimg, fn).items():
                    self.props[k] = v
            self.props['qemu.cpu'] = self.qemu_cpu()
            self.props['qemu.tag'] = self.tag()

    def _unpack_properties(self, zip_file, zip_info):
        prop = zip_file.read(zip_info).decode("utf-8").splitlines()
        res = dict([a.split("=") for a in prop if "=" in a])
        return res

    def __str__(self):
        return "{}-{}".format(self.desc(), self.revision())

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
        return self.SHORT_TAG[self.tag()]

    def desc(self):
        """Descripton of this release."""
        return self.props.get("Pkg.Desc")

    def revision(self):
        """The revision of this release."""
        return self.props.get("Pkg.Revision")

    def build_id(self):
        """The build id, or revision of build id is not available."""
        if "Pkg.BuildId" in self.props:
            return self.props.get("Pkg.BuildId")
        return self.revision()

    def repo_friendly_name(self):
        prefix = self.api()
        if len(prefix) == 0:
            prefix = self.codename().lower()
        return "{}-{}-{}".format(prefix, self.short_tag(), self.short_abi())

    def is_system_image(self):
        return "System Image" in self.desc()

    def is_emulator(self):
        return "Android Emulator" in self.desc()

    def logger_flags(self):
        if "arm" in self.qemu_cpu():
            return "-logcat *:V -show-kernel"
        else:
            return "-shell-serial file:/tmp/android-unknown/kernel.log -logcat-output /tmp/android-unknown/logcat.log"

    def copy(self, path):
        return shutil.copy2(self.fname, path)


    def extract(self, path):
        zip_file = zipfile.ZipFile(self.fname)
        print("Extracting: {} -> {}".format(self.fname, path))
        for info in tqdm(iterable=zip_file.infolist(), total=len(zip_file.infolist())):
            filename = zip_file.extract(info, path=path)
            mode = info.external_attr >> 16
            if mode:
                os.chmod(filename, mode)
