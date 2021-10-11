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
from pathlib import Path

from emu.utils import download

ANDROID_REPOSITORY = os.environ.get("ANDROID_REPOSITORY", "https://dl.google.com")

class PlatformTools(object):
    """The platform tools zip file. It will be downloaded on demand."""

    # Platform tools, needed to get adb.
    PLATFORM_TOOLS_URL = (
        '%s/android/repository/platform-tools_r29.0.5-linux.zip' % ANDROID_REPOSITORY
    )
    PLATFORM_TOOLS_ZIP = "platform-tools-latest-linux.zip"

    def __init__(self, fname=None):
        self.platform = fname

    def extract_adb(self, dest):
        if not self.platform:
            self.platform = self.download()
        with zipfile.ZipFile(self.platform, "r") as plzip:
            plzip.extract("platform-tools/adb", dest)

    def download(self, dest=None):
        """Downloads the platform tools zip to the given destination"""
        dest = dest or Path.cwd() / PlatformTools.PLATFORM_TOOLS_ZIP
        print(f"Downloading platform tools to {dest}")
        return download(PlatformTools.PLATFORM_TOOLS_URL, dest)
