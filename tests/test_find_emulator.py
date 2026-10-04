# Copyright 2026 The Android Open Source Project
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
"""Unit tests for find_emulator: a channel includes the more stable channels
below it, as it does for sdkmanager."""
import unittest.mock as mock

import pytest
import requests

import emu.emu_downloads_menu as menu


def _emu_pkg(channel, version, hostos="linux"):
    """Build an emulator <remotePackage> snippet shaped like the real SDK XML."""
    major, minor, micro = version.split(".")
    return f"""
<remotePackage path="emulator">
  <revision><major>{major}</major><minor>{minor}</minor><micro>{micro}</micro></revision>
  <uses-license ref="android-sdk-license"/>
  <channelRef ref="{channel}"/>
  <archives>
    <archive><complete><url>emulator-{version}.zip</url></complete><host-os>{hostos}</host-os></archive>
  </archives>
</remotePackage>"""


def _mock_repo(monkeypatch, packages):
    xml = """<?xml version="1.0" ?>
<sdk-repository>
  <license id="android-sdk-license" type="text">Terms</license>
  {}
</sdk-repository>""".format("".join(packages))

    def mock_get(url):
        return mock.MagicMock(content=xml, status_code=200)

    monkeypatch.setattr(requests, "get", mock_get)


# The version numbers below are made up: only their order and the channel they
# are published on matter.


@pytest.fixture
def stable_and_dev(monkeypatch):
    """What the repository usually holds: the pre-release emulator is published
    on channel-2, and nothing on channel-3."""
    _mock_repo(
        monkeypatch,
        [_emu_pkg("channel-2", "2.0.0"), _emu_pkg("channel-0", "1.0.0")],
    )


@pytest.mark.parametrize(
    "channel, expected",
    [
        ("stable", ["stable 1.0.0"]),
        ("beta", ["stable 1.0.0"]),
        ("dev", ["dev 2.0.0"]),
        ("canary", ["dev 2.0.0"]),
        ("all", ["dev 2.0.0", "stable 1.0.0"]),
    ],
)
def test_channel_includes_more_stable_channels(stable_and_dev, channel, expected):
    assert [str(x) for x in menu.find_emulator(channel)] == expected


def test_canary_prefers_newest_release(monkeypatch):
    _mock_repo(
        monkeypatch,
        [
            _emu_pkg("channel-0", "1.0.0"),
            _emu_pkg("channel-3", "1.10.0"),
            _emu_pkg("channel-2", "1.9.0"),
        ],
    )
    # Compared as numbers: 1.10.0 is newer than 1.9.0.
    assert [str(x) for x in menu.find_emulator("canary")] == ["canary 1.10.0"]
    assert [str(x) for x in menu.find_emulator("dev")] == ["dev 1.9.0"]


def test_canary_gives_stable_when_it_is_the_newest(monkeypatch):
    _mock_repo(
        monkeypatch,
        [_emu_pkg("channel-3", "1.0.0"), _emu_pkg("channel-0", "2.0.0")],
    )
    assert [str(x) for x in menu.find_emulator("canary")] == ["stable 2.0.0"]


def test_stable_does_not_include_less_stable_channels(monkeypatch):
    _mock_repo(monkeypatch, [_emu_pkg("channel-2", "2.0.0")])
    with pytest.raises(menu.EmulatorNotFoundException):
        menu.find_emulator("stable")


def test_emulator_without_linux_build_is_skipped(monkeypatch):
    _mock_repo(
        monkeypatch,
        [_emu_pkg("channel-2", "2.0.0", hostos="macosx"), _emu_pkg("channel-0", "1.0.0")],
    )
    assert [str(x) for x in menu.find_emulator("canary")] == ["stable 1.0.0"]


def test_unknown_channel_finds_nothing(stable_and_dev):
    with pytest.raises(menu.EmulatorNotFoundException):
        menu.find_emulator("nightly")
