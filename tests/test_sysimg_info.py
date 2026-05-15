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
"""Unit tests for the SDK-XML-driven SysImgInfo and the
zip-driven SystemImageReleaseZip helpers, focused on:

- API >= 33 letter mapping and api-level parsing ("36", "36.1", "37.0", "36x").
- 16 KB-page variant detection from the path's sort segment.
- Pre-release codename / ext-SDK detection.
- URL construction for the various sort_base shapes.
- SystemImageReleaseZip multi-tag SystemImage.TagId parsing.
"""
import xml.etree.ElementTree as ET

import pytest

from emu.android_release_zip import SystemImageReleaseZip
from emu.emu_downloads_menu import SysImgInfo


# --------------------------------------------------------------------------- #
# SysImgInfo helpers
# --------------------------------------------------------------------------- #

_LICENSES = {"android-sdk-license": object()}


def _pkg(path, api_level, abi, codename=None, tag_id="google_apis", url="zip.zip"):
    """Build a <remotePackage> Element shaped like the real SDK XML."""
    cn = f"<codename>{codename}</codename>" if codename else ""
    return ET.fromstring(
        f"""
<remotePackage path="{path}">
  <type-details>
    <api-level>{api_level}</api-level>
    {cn}
    <tag><id>{tag_id}</id></tag>
    <abi>{abi}</abi>
  </type-details>
  <uses-license ref="android-sdk-license"/>
  <archives>
    <archive><complete><url>{url}</url></complete></archive>
  </archives>
</remotePackage>
""".strip()
    )


# --------------------------------------------------------------------------- #
# SysImgInfo.letter / api_major / is_preview / is_ext_sdk
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "api_level, expected_letter, expected_major",
    [
        ("33", "T", 33),
        ("34", "U", 34),
        ("35", "V", 35),
        ("36", "B", 36),
        ("37", "C", 37),
        ("36.0", "B", 36),
        ("36.1", "B", 36),
        ("37.0", "C", 37),
        ("36x", "B", 36),  # ext-SDK: still maps to the parent letter
    ],
)
def test_letter_and_api_major_for_modern_apis(api_level, expected_letter, expected_major):
    info = SysImgInfo(
        _pkg(f"system-images;android-{api_level};google_apis;x86_64", api_level, "x86_64"),
        _LICENSES,
    )
    assert info.letter == expected_letter
    assert info.api_major == expected_major


def test_letter_falls_back_to_api_string_when_unknown():
    """Unknown future API must not silently become 'A' (the historical trap)."""
    info = SysImgInfo(
        _pkg("system-images;android-99;google_apis;x86_64", "99", "x86_64"),
        _LICENSES,
    )
    assert info.letter == "99"
    assert info.api_major == 99


def test_is_preview_true_when_codename_present():
    info = SysImgInfo(
        _pkg(
            "system-images;android-CinnamonBun;google_apis;x86_64",
            "37.0",
            "x86_64",
            codename="CinnamonBun",
        ),
        _LICENSES,
    )
    assert info.is_preview is True


def test_is_preview_false_for_released_build():
    info = SysImgInfo(
        _pkg("system-images;android-36;google_apis;x86_64", "36", "x86_64"),
        _LICENSES,
    )
    assert info.is_preview is False


def test_is_ext_sdk_true_when_api_level_ends_with_x():
    info = SysImgInfo(
        _pkg("system-images;android-36-ext19;google_apis;x86_64", "36x", "x86_64"),
        _LICENSES,
    )
    assert info.is_ext_sdk is True


def test_is_ext_sdk_false_for_normal_release():
    info = SysImgInfo(
        _pkg("system-images;android-36;google_apis;x86_64", "36", "x86_64"),
        _LICENSES,
    )
    assert info.is_ext_sdk is False


# --------------------------------------------------------------------------- #
# SysImgInfo: 16 KB-page variant detection from path
# --------------------------------------------------------------------------- #


def test_is_16k_true_when_path_sort_ends_with_ps16k():
    info = SysImgInfo(
        _pkg(
            "system-images;android-36;google_apis_ps16k;x86_64",
            "36",
            "x86_64",
            url="x86_64-ps16k-36_r07.zip",
        ),
        _LICENSES,
    )
    assert info.is_16k is True
    assert info.tag == "google_apis"  # sort_base, without the _ps16k suffix
    assert info.image_name() == "sys-36-google-x64-ps16k"
    assert " ps16k" in str(info)


def test_is_16k_false_for_regular_4kb_variant():
    info = SysImgInfo(
        _pkg(
            "system-images;android-36;google_apis;x86_64",
            "36",
            "x86_64",
            url="x86_64-36_r07.zip",
        ),
        _LICENSES,
    )
    assert info.is_16k is False
    assert info.image_name() == "sys-36-google-x64"
    assert " ps16k" not in str(info)


# --------------------------------------------------------------------------- #
# SysImgInfo: URL construction
# --------------------------------------------------------------------------- #


def test_url_for_ps16k_uses_sort_base_directory():
    """16 KB zips live under sys-img/<sort_base>/, not sys-img/<sort_base_ps16k>/."""
    info = SysImgInfo(
        _pkg(
            "system-images;android-36;google_apis_playstore_ps16k;x86_64",
            "36",
            "x86_64",
            url="x86_64-playstore-ps16k-36_r07.zip",
        ),
        _LICENSES,
    )
    assert info.url == (
        "https://dl.google.com/android/repository/sys-img/google_apis_playstore/"
        "x86_64-playstore-ps16k-36_r07.zip"
    )


def test_url_for_default_sort_remaps_to_android_directory():
    """The legacy 'default' sort segment is served from the 'android' subdir."""
    info = SysImgInfo(
        _pkg(
            "system-images;android-30;default;x86_64",
            "30",
            "x86_64",
            tag_id="default",
            url="x86_64-30_r02.zip",
        ),
        _LICENSES,
    )
    assert info.tag == "android"
    assert info.url == (
        "https://dl.google.com/android/repository/sys-img/android/x86_64-30_r02.zip"
    )


# --------------------------------------------------------------------------- #
# SystemImageReleaseZip.tag() / is_16k() — multi-tag SystemImage.TagId parsing
# --------------------------------------------------------------------------- #


def _release_zip(tag_id):
    """Construct a SystemImageReleaseZip with only the props dict populated."""
    z = SystemImageReleaseZip.__new__(SystemImageReleaseZip)
    z.props = {"SystemImage.TagId": tag_id}
    return z


@pytest.mark.parametrize(
    "tag_id, expected_tag, expected_is_16k",
    [
        ("google_apis", "google_apis", False),
        ("google_apis_playstore", "google_apis_playstore", False),
        ("google_apis,page_size_16kb", "google_apis", True),
        ("page_size_16kb,google_apis", "google_apis", True),  # other order seen for Baklava
        ("google_apis_playstore,page_size_16kb", "google_apis_playstore", True),
        ("default", "android", False),
        ("", "android", False),
    ],
)
def test_release_zip_tag_and_is_16k(tag_id, expected_tag, expected_is_16k):
    z = _release_zip(tag_id)
    assert z.tag() == expected_tag
    assert z.is_16k() is expected_is_16k
