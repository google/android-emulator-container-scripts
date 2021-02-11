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
import os
import zipfile

from emu.utils import download

# Platform tools, needed to get adb.
PLATFORM_TOOLS_URL = "https://dl.google.com/android/repository/platform-tools_r29.0.5-linux.zip"


class PlatformTools(object):
    """The platform tools zip file. It will be downloaded on demand."""

    def __init__(self, fname=None):
        self.platform = fname

    def extract_adb(self, dest):
        if not self.platform:
            self.platform = self.download()
        with zipfile.ZipFile(self.platform, "r") as plzip:
            plzip.extract("platform-tools/adb", dest)

    def download(self, dest=None):
        dest = dest or os.path.join(os.getcwd(), "platform-tools-latest-linux.zip")
        print("Downloading platform tools to {}".format(dest))
        return download(PLATFORM_TOOLS_URL, dest)
