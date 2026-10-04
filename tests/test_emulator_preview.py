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
"""Unit tests for Emulator Preview support, focused on:

- EmuInfo parsing of the "emulators;latest" / "emulators;<build-id>" packages.
- find_emulator picking the latest preview for API 37+ system images.
- Menu filtering and ordering in select_emulator.
- Preview detection from the zip, and the emulator/system-image pairing check.
- The launcher template leaving out "-qemu -append" for preview builds.
"""
import os
import types
import unittest.mock as mock
import zipfile

import pytest
import requests

import emu.emu_docker as emu_docker
import emu.emu_downloads_menu as menu
from emu.android_release_zip import AndroidReleaseZip
from emu.template_writer import TemplateWriter


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def _emu_pkg(path, channel, version, url, preview=None, display_name=None, hostos="linux"):
    """Build a <remotePackage> snippet shaped like the real SDK XML."""
    major, minor, micro = version.split(".")
    prev = f"<preview>{preview}</preview>" if preview else ""
    name = f"<display-name>{display_name}</display-name>" if display_name else ""
    return f"""
<remotePackage path="{path}">
  <revision><major>{major}</major><minor>{minor}</minor><micro>{micro}</micro>{prev}</revision>
  {name}
  <uses-license ref="android-sdk-license"/>
  <channelRef ref="{channel}"/>
  <archives>
    <archive><complete><url>{url}</url></complete><host-os>{hostos}</host-os></archive>
  </archives>
</remotePackage>"""


_REPO_XML = """<?xml version="1.0" ?>
<sdk-repository>
  <license id="android-sdk-license" type="text">Terms</license>
  {packages}
  <remotePackage path="platform-tools">
    <revision><major>36</major><minor>0</minor><micro>0</micro></revision>
    <uses-license ref="android-sdk-license"/>
    <channelRef ref="channel-0"/>
    <archives>
      <archive><complete><url>platform-tools.zip</url></complete><host-os>linux</host-os></archive>
    </archives>
  </remotePackage>
</sdk-repository>
"""

_PREVIEW = "Android Emulator (Preview)"

# The version numbers below are made up: only their order, and the path and
# channel they are published on matter.
_PACKAGES = [
    # A pinned build comes first, as in the real repository: "latest" has to be
    # found by its path, not by its position.
    _emu_pkg("emulators;200", "channel-2", "0.2.0", "emu-preview-200.zip", display_name=_PREVIEW),
    _emu_pkg("emulator", "channel-2", "2.0.0", "emu-dev.zip", display_name="Android Emulator"),
    _emu_pkg("emulators;300", "channel-2", "0.3.0", "emu-preview-300.zip", display_name=_PREVIEW),
    _emu_pkg("emulators;latest", "channel-2", "0.3.0", "emu-preview-300.zip", display_name=_PREVIEW + " (latest)"),
    _emu_pkg("emulator", "channel-0", "1.0.0", "emu-stable.zip", display_name="Android Emulator"),
    _emu_pkg("emulators;400", "channel-2", "0.4.0", "emu-preview-mac.zip", hostos="macosx"),
]


def _mock_repo(monkeypatch, packages):
    xml = _REPO_XML.format(packages="".join(packages))

    def mock_get(url):
        return mock.MagicMock(content=xml, status_code=200)

    monkeypatch.setattr(requests, "get", mock_get)


@pytest.fixture
def emu_repo(monkeypatch):
    _mock_repo(monkeypatch, _PACKAGES)


def _sys_img(api):
    """A stand-in for SysImgInfo with just what the emulator menu looks at."""
    return types.SimpleNamespace(api=str(api), api_major=int(float(api)))


def _emu_zip(temp_dir, description, name="emulator.zip"):
    path = temp_dir / name
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr(
            "emulator/source.properties",
            f"Pkg.Desc={description}\nPkg.Revision=1.2.3\n",
        )
    return path


# --------------------------------------------------------------------------- #
# EmuInfo / get_emus_info
# --------------------------------------------------------------------------- #


def test_get_emus_info_includes_preview_packages(emu_repo):
    paths = [x.path for x in menu.get_emus_info()]
    assert paths == [
        "emulators;200",
        "emulator",
        "emulators;300",
        "emulators;latest",
        "emulator",
        "emulators;400",
    ]


def test_regular_emulator_is_not_preview(emu_repo):
    stable = menu.find_emulator("stable")[0]
    assert stable.is_preview is False
    assert stable.version == "1.0.0"
    assert str(stable) == "stable 1.0.0"
    assert stable.download_name() == "emulator-1.0.0.zip"


def test_preview_is_recognized_by_path(emu_repo):
    preview = [x for x in menu.get_emus_info() if x.is_preview]
    assert [x.version for x in preview] == ["0.2.0", "0.3.0", "0.3.0", "0.4.0"]
    assert str(preview[0]) == "preview 0.2.0"


def test_preview_download_does_not_share_a_name_with_regular_emulator(emu_repo):
    # Both emulators can carry the same version, and existing files are reused.
    preview = [x for x in menu.get_emus_info() if x.is_preview][0]
    assert preview.download_name() == "emulator-preview-0.2.0.zip"


def test_preview_build_id_is_added_to_version(monkeypatch):
    _mock_repo(
        monkeypatch,
        [_emu_pkg("emulators;latest", "channel-2", "0.0.1", "emu.zip", preview="200")],
    )
    assert menu.get_emus_info()[0].version == "0.0.1-200"


def test_display_name_defaults_when_missing(emu_repo):
    by_path = {x.path: x for x in menu.get_emus_info()}
    assert by_path["emulators;latest"].display_name == "Android Emulator (Preview) (latest)"
    assert by_path["emulators;400"].display_name == "Android Emulator"


# --------------------------------------------------------------------------- #
# find_emulator
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("channel", ["stable", "canary", "all"])
@pytest.mark.parametrize("api_major", [37, 38])
def test_recent_image_gets_latest_preview_whatever_the_channel(emu_repo, channel, api_major):
    found = menu.find_emulator(channel, api_major)
    assert [x.path for x in found] == ["emulators;latest"]


@pytest.mark.parametrize("api_major", [None, 28, 36])
@pytest.mark.parametrize(
    "channel, expected",
    [
        ("stable", ["stable 1.0.0"]),
        ("canary", ["dev 2.0.0"]),
        ("all", ["dev 2.0.0", "stable 1.0.0"]),
    ],
)
def test_older_image_gets_regular_emulator(emu_repo, channel, expected, api_major):
    assert [str(x) for x in menu.find_emulator(channel, api_major)] == expected


def test_dev_channel_does_not_pull_in_preview(monkeypatch):
    # The preview is published on the dev channel, but it is not what "dev" means.
    _mock_repo(monkeypatch, [p for p in _PACKAGES if "emu-dev.zip" not in p])
    assert [str(x) for x in menu.find_emulator("dev", 36)] == ["stable 1.0.0"]


def test_preview_is_not_a_channel(emu_repo):
    with pytest.raises(menu.EmulatorNotFoundException):
        menu.find_emulator("preview")


def test_recent_image_falls_back_to_channel_without_preview(monkeypatch):
    _mock_repo(monkeypatch, [p for p in _PACKAGES if "emulators;" not in p])
    assert [str(x) for x in menu.find_emulator("stable", 37)] == ["stable 1.0.0"]


# --------------------------------------------------------------------------- #
# emulator_supports_image / select_emulator / list_all_downloads
# --------------------------------------------------------------------------- #


def _latest_preview():
    return menu.find_emulator("stable", 37)[0]


@pytest.mark.parametrize(
    "api, supported",
    [("28", False), ("36", False), ("36.1", False), ("37", True), ("37.0", True), ("38", True)],
)
def test_preview_supports_only_recent_images(emu_repo, api, supported):
    assert menu.emulator_supports_image(_latest_preview(), _sys_img(api)) is supported


def test_regular_emulator_supports_any_image(emu_repo):
    stable = menu.find_emulator("stable")[0]
    assert menu.emulator_supports_image(stable, _sys_img("28")) is True
    assert menu.emulator_supports_image(stable, _sys_img("37")) is True


def test_preview_supported_when_no_image_given(emu_repo):
    assert menu.emulator_supports_image(_latest_preview(), None) is True


@pytest.fixture
def selection_menu(monkeypatch):
    """Captures what the emulator menu displays, and picks the first entry."""
    shown = []

    def get_selection(display, title):
        shown.extend(display)
        return 0

    monkeypatch.setattr(menu.SelectionMenu, "get_selection", get_selection)
    return shown


def test_select_emulator_hides_preview_for_older_image(emu_repo, selection_menu, capsys):
    picked = menu.select_emulator(_sys_img("36"))

    assert selection_menu == [
        "EMU dev 2.0.0 (Android Emulator)",
        "EMU stable 1.0.0 (Android Emulator)",
    ]
    assert str(picked) == "dev 2.0.0"
    assert "Emulator Preview is not offered for API 36" in capsys.readouterr().out


def test_select_emulator_lists_preview_first_for_recent_image(emu_repo, selection_menu, capsys):
    picked = menu.select_emulator(_sys_img("37"))

    # The regular emulator still runs API 37, and a pinned preview build can be
    # picked on purpose, so both stay in the menu below the latest preview.
    assert selection_menu == [
        "EMU preview 0.3.0 (Android Emulator (Preview) (latest))",
        "EMU preview 0.2.0 (Android Emulator (Preview))",
        "EMU preview 0.3.0 (Android Emulator (Preview))",
        "EMU dev 2.0.0 (Android Emulator)",
        "EMU stable 1.0.0 (Android Emulator)",
    ]
    assert picked.path == "emulators;latest"
    assert "not offered" not in capsys.readouterr().out


def test_select_emulator_without_image_keeps_repository_order(emu_repo, selection_menu, capsys):
    menu.select_emulator()

    assert selection_menu[0] == "EMU preview 0.2.0 (Android Emulator (Preview))"
    assert len(selection_menu) == 5
    assert "not offered" not in capsys.readouterr().out


def test_select_emulator_returns_none_on_exit(emu_repo, monkeypatch):
    # SelectionMenu reports the "Exit" entry as one past the last item.
    monkeypatch.setattr(
        menu.SelectionMenu, "get_selection", lambda display, title: len(display)
    )
    assert menu.select_emulator() is None


def test_list_all_downloads_labels_preview(emu_repo, monkeypatch, capsys):
    monkeypatch.setattr(menu, "get_images_info", lambda arm: [])

    menu.list_all_downloads(False)

    lines = capsys.readouterr().out.splitlines()
    assert f"EMU stable 1.0.0 linux {menu.ANDROID_REPOSITORY}/android/repository/emu-stable.zip" in lines
    assert f"EMU preview 0.2.0 linux {menu.ANDROID_REPOSITORY}/android/repository/emu-preview-200.zip" in lines
    # The regular emulator is the only one left under its channel name.
    assert [line for line in lines if line.startswith("EMU dev")] == [
        f"EMU dev 2.0.0 linux {menu.ANDROID_REPOSITORY}/android/repository/emu-dev.zip"
    ]


# --------------------------------------------------------------------------- #
# AndroidReleaseZip.is_preview_emulator
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "description, is_preview",
    [
        ("Android Emulator", False),
        ("Android Emulator (Preview)", True),
        ("Android SDK Platform-Tools (Preview)", False),
    ],
)
def test_is_preview_emulator(temp_dir, description, is_preview):
    zip_file = AndroidReleaseZip(_emu_zip(temp_dir, description))
    assert zip_file.is_preview_emulator() is is_preview


# --------------------------------------------------------------------------- #
# emu_docker._check_emulator_supports_image
# --------------------------------------------------------------------------- #


def _sys_docker_from_zip(api):
    """A stand-in for a SystemImageContainer built from a local zip."""
    return types.SimpleNamespace(
        system_image_info=None,
        system_image_zip=types.SimpleNamespace(api=lambda: api),
    )


def _sys_docker_from_info(api):
    """A stand-in for a SystemImageContainer whose zip is not downloaded yet."""
    return types.SimpleNamespace(system_image_info=_sys_img(api), system_image_zip=None)


@pytest.mark.parametrize("sys_docker", [_sys_docker_from_zip, _sys_docker_from_info])
@pytest.mark.parametrize("api", ["28", "36", "36.1"])
def test_check_rejects_preview_with_older_image(temp_dir, sys_docker, api):
    emulator = _emu_zip(temp_dir, "Android Emulator (Preview)", "emulator-preview.zip")

    with pytest.raises(Exception) as err:
        emu_docker._check_emulator_supports_image(emulator, sys_docker(api))

    assert "requires an API 37+ system image" in str(err.value)
    assert "emulator-preview.zip" in str(err.value)


def test_check_rejects_preview_when_zip_has_no_api_level(temp_dir):
    emulator = _emu_zip(temp_dir, "Android Emulator (Preview)")
    with pytest.raises(Exception):
        emu_docker._check_emulator_supports_image(emulator, _sys_docker_from_zip(""))


@pytest.mark.parametrize("sys_docker", [_sys_docker_from_zip, _sys_docker_from_info])
@pytest.mark.parametrize("api", ["37", "37.0", "38"])
def test_check_accepts_preview_with_recent_image(temp_dir, sys_docker, api):
    emulator = _emu_zip(temp_dir, "Android Emulator (Preview)")
    emu_docker._check_emulator_supports_image(emulator, sys_docker(api))


def test_check_accepts_regular_emulator_with_any_image(temp_dir):
    emulator = _emu_zip(temp_dir, "Android Emulator")
    emu_docker._check_emulator_supports_image(emulator, _sys_docker_from_zip("28"))
    emu_docker._check_emulator_supports_image(emulator, _sys_docker_from_zip("37"))


# --------------------------------------------------------------------------- #
# launch-emulator.sh template
# --------------------------------------------------------------------------- #

_QEMU_APPEND = 'LAUNCH_CMD+=("-qemu" "-append" "panic=1")'


def _launch_script(temp_dir, preview_emulator):
    writer = TemplateWriter(temp_dir)
    writer.write_template(
        "launch-emulator.sh",
        {"extra": "", "version": "1.0", "preview_emulator": preview_emulator},
    )
    return (temp_dir / "launch-emulator.sh").read_text()


def test_launcher_sets_panic_for_regular_emulator(temp_dir):
    assert _QEMU_APPEND in _launch_script(temp_dir, False)


def test_launcher_leaves_out_qemu_append_for_preview(temp_dir):
    assert _QEMU_APPEND not in _launch_script(temp_dir, True)


# --------------------------------------------------------------------------- #
# emu_docker.create_docker_image
# --------------------------------------------------------------------------- #


@pytest.fixture
def create_image(monkeypatch, temp_dir):
    """Runs create_docker_image with docker and the downloads stubbed out.

    Returns a function that takes the emulator argument and the api levels of
    the matching system images, and gives back the (api, emulator) pairs built.
    """
    built = []

    class FakeSystemImageContainer:
        def __init__(self, img, repo):
            self.system_image_info = img
            self.system_image_zip = None

        def available(self):
            return True

        def can_pull(self):
            return True

    class FakeEmulatorContainer:
        def __init__(self, emulator, sys_docker, *args):
            built.append((sys_docker.system_image_info.api, os.path.basename(str(emulator))))

        def build(self, dest):
            pass

    def find_emulator(channel, api_major=None):
        if api_major >= menu.MIN_API_PREVIEW_EMULATOR:
            descriptions = {"emulator-preview.zip": "Android Emulator (Preview)"}
        else:
            descriptions = {f"emulator-{channel}.zip": "Android Emulator"}
        return [
            mock.MagicMock(download=lambda n=name, d=desc: _emu_zip(temp_dir, d, n))
            for name, desc in descriptions.items()
        ]

    monkeypatch.setattr(emu_docker, "SystemImageContainer", FakeSystemImageContainer)
    monkeypatch.setattr(emu_docker, "EmulatorContainer", FakeEmulatorContainer)
    monkeypatch.setattr(emu_docker, "metrics_config", lambda args: mock.MagicMock())
    monkeypatch.setattr(menu, "find_emulator", mock.MagicMock(side_effect=find_emulator))

    def run(emuzip, apis, sys=False):
        monkeypatch.setattr(menu, "find_image", lambda regexpr: [_sys_img(a) for a in apis])
        args = types.SimpleNamespace(
            imgzip="some-image-regexp",
            emuzip=str(emuzip),
            repo="repo",
            dest=str(temp_dir),
            push=False,
            sys=sys,
            start=False,
            extra="",
            name=None,
        )
        emu_docker.create_docker_image(args)
        return built

    return run


def test_create_picks_emulator_per_system_image(create_image):
    assert create_image("stable", ["36", "37", "28", "38"]) == [
        ("36", "emulator-stable.zip"),
        ("37", "emulator-preview.zip"),
        ("28", "emulator-stable.zip"),
        ("38", "emulator-preview.zip"),
    ]
    # One lookup for the older images, one for the recent ones.
    assert menu.find_emulator.call_count == 2


def test_create_uses_given_zip_for_every_image(create_image, temp_dir):
    emulator = _emu_zip(temp_dir, "Android Emulator", "my-emulator.zip")

    assert create_image(emulator, ["36", "37"]) == [
        ("36", "my-emulator.zip"),
        ("37", "my-emulator.zip"),
    ]
    menu.find_emulator.assert_not_called()


def test_create_refuses_preview_zip_with_older_image(create_image, temp_dir):
    emulator = _emu_zip(temp_dir, "Android Emulator (Preview)", "my-preview.zip")

    with pytest.raises(Exception) as err:
        create_image(emulator, ["37", "36"])

    assert "my-preview.zip was paired with API 36" in str(err.value)


def test_create_sys_only_does_not_look_up_an_emulator(create_image):
    assert create_image("stable", ["37"], sys=True) == []
    menu.find_emulator.assert_not_called()
