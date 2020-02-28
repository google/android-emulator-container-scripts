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


Arguments = collections.namedtuple("Args", "img, dest, repo")


@pytest.mark.slow
@pytest.mark.e2e
def test_build_container():
    assert docker.from_env().ping()
    # Make sure we accept all licenses,
    with TempDir() as tmp:
        args = Arguments("(P google_apis_playstore x86_64)|(Q google_apis x86_64)", tmp, "us.gcr.io/emu-dev-tst")
        cloud_build(args)
        expected_files = [
            "cloudbuild.yaml",
            "README.MD",
            "p-playstore-x64",
            "p-playstore-x64-no-metrics",
            "q-google-x64",
            "q-google-x64-no-metrics",
        ]
        for fname in expected_files:
            assert os.path.exists(os.path.join(tmp, fname))
