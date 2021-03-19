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
"""End 2 end test that builds every image.

   This is super expensive..
"""

import collections
import os

import docker
import pytest
from emu.cloud_build import cloud_build
from utils import TempDir
import shutil
import subprocess

Arguments = collections.namedtuple("Args", "emuzip, img, dest, repo, git, sys")


@pytest.mark.slow
@pytest.mark.e2e
def test_build_cloud_only_emu():
    assert docker.from_env().ping()
    # Make sure we accept all licenses,
    with TempDir() as tmp:
        args = Arguments(
            "canary", "Q google_apis x86_64", tmp, "us-docker.pkg.dev/android-emulator-268719/images", False, False
        )
        cloud_build(args)
        expected_files = [
            "cloudbuild.yaml",
            "README.MD",
            "29-google-x64",
            "29-google-x64-no-metrics",
        ]
        for file_name in expected_files:
            assert os.path.exists(os.path.join(tmp, file_name)), "cannot find {} in {}".format(file_name, tmp)


@pytest.mark.slow
@pytest.mark.e2e
def test_build_cloud_only_sys():
    assert docker.from_env().ping()
    # Make sure we accept all licenses,
    with TempDir() as tmp:
        args = Arguments(
            "canary", "Q google_apis x86_64", tmp, "us-docker.pkg.dev/android-emulator-268719/images", False, True
        )
        cloud_build(args)
        expected_files = [
            "cloudbuild.yaml",
            "README.MD",
            "sys-29-google-x64",
        ]
        for file_name in expected_files:
            assert os.path.exists(os.path.join(tmp, file_name)), "cannot find {} in {}".format(file_name, tmp)
