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
import tempfile
from contextlib import closing
from distutils.spawn import find_executable


def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('localhost', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def find_adb():
    adb_loc = os.path.join(os.environ.get("ANDROID_SDK_ROOT", ""), "platform-tools", "adb")
    if not (os.path.exists(adb_loc) and os.access(adb_loc, os.X_OK)):
        adb_loc = find_executable("adb")
    return adb_loc

class TempDir(object):
    """Creates a temporary directory that automatically is deleted."""

    def __enter__(self):
        self.tmpdir = tempfile.mkdtemp("unittest")
        return self.tmpdir

    def __exit__(self, exc_type, exc_value, tb):
        shutil.rmtree(self.tmpdir)
