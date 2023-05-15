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
import tempfile
from pathlib import Path
import emu.emu_downloads_menu as menu
import unittest.mock as mock
import pytest


def test_do_not_download_existing(temp_dir, monkeypatch):
    def mock_get(url, timeout, stream):
        assert False, "should not be called!"

    monkeypatch.setattr(menu.requests, "get", mock_get)

    url = "https://foo/bar"
    dest = temp_dir / "ignored.zip"
    with open(dest, "w", encoding="utf-8") as f:
        f.write("Hello world")

    dwnload = menu.download(url, dest)

    assert dwnload == dest
    assert dwnload.exists()


def test_downloads_if_not_exist(temp_dir, monkeypatch):
    def mock_get(url, timeout, stream):
        return mock.MagicMock(content=b"dummy_data")

    monkeypatch.setattr(menu.requests, "get", mock_get)

    url = "https://foo/bar"
    dest = temp_dir / "down.zip"
    dwnload = menu.download(url, dest)

    assert dwnload == dest
    assert dwnload.exists()
