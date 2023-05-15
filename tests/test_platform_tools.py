# Copyright 2023 The Android Open Source Project
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

import unittest.mock as mock

import pytest

from emu.platform_tools import PlatformTools


@pytest.fixture
def mock_zip():
    with mock.patch("zipfile.ZipFile") as mock_zip:
        yield mock_zip


@pytest.fixture
def platform_tools(mock_zip):
    return PlatformTools("/tmp/tools.zip")


def test_extract_unzips_something(mock_zip, platform_tools):
    """Unzips adb"""
    platform_tools.extract_adb("foo")

    mock_zip.assert_called_with("/tmp/tools.zip", "r")
    zip_handle = mock_zip.return_value.__enter__.return_value
    zip_handle.extract.assert_called_with("platform-tools/adb", "foo")
