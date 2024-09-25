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

# Minimal dependency script to query a set of
# publically available emulator and system image zip files.

import logging
import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import click
import requests
from consolemenu import SelectionMenu
from emu.utils import download
from emu.docker_config import DockerConfig

SYSIMG_REPOS = [
    "https://dl.google.com/android/repository/sys-img/android/sys-img2-1.xml",
    "https://dl.google.com/android/repository/sys-img/google_apis/sys-img2-1.xml",
    "https://dl.google.com/android/repository/sys-img/google_apis_playstore/sys-img2-1.xml",
    "https://dl.google.com/android/repository/sys-img/google_atd/sys-img2-1.xml",
    "https://dl.google.com/android/repository/sys-img/android-tv/sys-img2-1.xml",
]

EMU_REPOS = ["https://dl.google.com/android/repository/repository2-1.xml"]

CHANNEL_MAPPING = {
    "channel-0": "stable",
    "channel-1": "beta",
    "channel-2": "dev",
    "channel-3": "canary",
}

API_LETTER_MAPPING = {
    "10": "G",
    "15": "I",
    "16": "J",
    "17": "J",
    "18": "J",
    "19": "K",
    "21": "L",
    "22": "L",
    "23": "M",
    "24": "N",
    "25": "N",
    "26": "O",
    "27": "O",
    "28": "P",
    "29": "Q",
    "30": "R",
    "31": "S",
    "32": "S",
    "33": "T",
    "34": "U",
    "35": "V",
}

# Older versions might not work as expected.
MIN_REL_I386 = "K"
MIN_REL_X64 = "O"


class License(object):
    """Represents a license."""

    def __init__(self, license):
        self.name = license.attrib["id"]
        self.text = license.text
        self.cfg = DockerConfig()

    def accept(self):
        agree = "\n\n".join([self.text, "Do you accept the license?"])
        if not self.is_accepted():
            if not click.confirm(agree):
                raise Exception("License not accepted.")
            self.cfg.accept_license(self.name)

        return True

    def is_accepted(self):
        return self.cfg.accepted_license(self.name)

    def force_accept(self):
        self.cfg.accept_license(self.name)

    def __str__(self):
        # encode to utf-8 for python 2
        return str(self.text.encode("utf-8"))

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.name == other.name


class LicensedObject(object):
    """A dowloadable object for which a license needs to be accepted."""

    def __init__(self, pkg, licenses):
        self.license = licenses[pkg.find("uses-license").attrib["ref"]]

    def download(self, url, dest):
        """ "Downloads the released pacakage to the dest."""
        if self.license.accept():
            return download(url, dest)


class SysImgInfo(LicensedObject):
    """Provides information about a released system image."""

    SHORT_MAP = {
        "armeabi-v7a": "a32",
        "arm64-v8a": "a64",
        "x86_64": "x64",
        "x86": "x86",
    }
    SHORT_TAG = {
        "android": "aosp",
        "google_apis": "google",
        "google_apis_playstore": "playstore",
        "google_atd": "google_atd",
        "google_ndk_playstore": "ndk_playstore",
        "android-tv": "tv",
    }

    def __init__(self, pkg, licenses):
        super(SysImgInfo, self).__init__(pkg, licenses)
        details = pkg.find("type-details")
        self.api = details.find("api-level").text

        codename = details.find("codename")
        if codename is None:
            if self.api in API_LETTER_MAPPING:
                self.letter = API_LETTER_MAPPING[self.api]
            else:
                self.letter = "A"  # A indicates unknown code.
        else:
            self.letter = codename.text

        self.tag = details.find("tag").find("id").text

        if self.tag == "default":
            self.tag = "android"
        self.abi = details.find("abi").text

        # prefer a url for a Linux host in case there are multiple
        url_element = pkg.find(".//archive[host-os='linux']/complete/url")
        # fallback is to pick the first url
        if url_element is None:
            url_element = pkg.find(".//url")
        self.zip = url_element.text

        self.url = "https://dl.google.com/android/repository/sys-img/%s/%s" % (
            self.tag,
            self.zip,
        )

    def short_tag(self):
        return self.SHORT_TAG[self.tag]

    def short_abi(self):
        return self.SHORT_MAP[self.abi]

    def image_name(self):
        return "sys-{}-{}-{}".format(self.api, self.short_tag(), self.short_abi())

    def download_name(self):
        return "sys-img-{}-{}-{}-{}.zip".format(
            self.tag, self.api, self.letter, self.abi
        )

    def download(self, dest=Path.cwd()):
        dest = dest / self.download_name()
        print(
            f"Downloading system image: {self.tag} {self.api} {self.letter} {self.abi} to {dest}"
        )

        return super(SysImgInfo, self).download(self.url, dest)

    def __str__(self):
        return "{} {} {}".format(self.letter, self.tag, self.abi)


class EmuInfo(LicensedObject):
    """Provides information about a released emulator."""

    def __init__(self, pkg, licenses):
        super(EmuInfo, self).__init__(pkg, licenses)
        rev = pkg.find("revision")

        rev_major = rev.find("major").text
        rev_minor = rev.find("minor").text
        rev_micro = rev.find("micro").text

        archives = pkg.find("archives")
        channel = pkg.find("channelRef")

        self.channel = CHANNEL_MAPPING[channel.attrib["ref"]]

        self.version = "%s.%s.%s" % (rev_major, rev_minor, rev_micro)
        self.urls = {}

        for archive in archives:
            url = archive.find(".//url").text
            hostos = archive.find("host-os").text
            self.urls[hostos] = "https://dl.google.com/android/repository/%s" % url

    def download_name(self):
        return "emulator-{}.zip".format(self.version)

    def download(self, hostos="linux", dest=None):
        """Downloads the released pacakage for the given os to the dest."""
        dest = dest or Path.cwd() / self.download_name()
        print(f"Downloading emulator: {self.channel} {self.version} to {dest}")

        return super(EmuInfo, self).download(self.urls[hostos], dest)

    def __str__(self):
        return "{} {}".format(self.channel, self.version)


def get_images_info(arm=False):
    """Gets all the publicly available system images from the Android Image Repos.

    Returns a list of AndroidSystemImages that were found and (hopefully) can boot."""
    xml = []
    for url in SYSIMG_REPOS:
        response = requests.get(url)
        if response.status_code == 200:
            xml.append(response.content)

    licenses = [License(p) for x in xml for p in ET.fromstring(x).findall("license")]
    licenses = dict([(x.name, x) for x in [y for y in licenses]])

    xml = [ET.fromstring(x).findall("remotePackage") for x in xml]
    # Flatten the list of lists into a system image objects.
    infos = [SysImgInfo(item, licenses) for sublist in xml for item in sublist]
    # Filter only for intel images that we know that work
    x86_64_imgs = [
        info for info in infos if info.abi == "x86_64" and info.letter >= MIN_REL_X64
    ]
    x86_imgs = [
        info for info in infos if info.abi == "x86" and info.letter >= MIN_REL_I386
    ]
    slow = []
    if arm:
        slow = [info for info in infos if info.abi.startswith("arm")]
    all_imgs = sorted(x86_64_imgs + x86_imgs + slow, key=lambda x: x.api + x.tag)
    # Filter out windows/darwin images.
    return [i for i in all_imgs if "windows" not in i.url and "darwin" not in i.url]


class ImageNotFoundException(Exception):
    pass


class EmulatorNotFoundException(Exception):
    pass


def find_image(regexpr):
    reg = re.compile(regexpr)
    all_images = get_images_info(True)
    matches = [img for img in all_images if reg.match(str(img))]
    logging.info(
        "Found %s matching images: %s from %s",
        regexpr,
        [str(x) for x in matches],
        [str(x) for x in all_images],
    )
    if not matches:
        raise ImageNotFoundException(
            f"No system image found matching {regexpr}. Run the list command to list available images"
        )
    return matches


def find_emulator(channel):
    """Displayes an interactive menu to select a released emulator binary.

    Returns a ImuInfo object with the choice or None if the user aborts."""
    emu_infos = [
        x
        for x in get_emus_info()
        if "linux" in x.urls and (channel == "all" or x.channel == channel)
    ]
    logging.info("Found %s matching images: %s", channel, [str(x) for x in emu_infos])
    if not emu_infos:
        raise EmulatorNotFoundException(f"No emulator found in channel {channel}")
    return emu_infos


def get_emus_info():
    """Gets all the publicly available emulator builds.

    Returns a list of EmuInfo items that were found."""
    xml = []
    for url in EMU_REPOS:
        response = requests.get(url)
        if response.status_code == 200:
            xml.append(response.content)

    licenses = [License(p) for x in xml for p in ET.fromstring(x).findall("license")]
    licenses = dict([(x.name, x) for x in [y for y in licenses]])
    xml = [
        [
            p
            for p in ET.fromstring(x).findall("remotePackage")
            if "emulator" == p.attrib["path"]
        ]
        for x in xml
    ]
    # Flatten the list of lists into a system image objects.
    infos = [EmuInfo(item, licenses) for sublist in xml for item in sublist]
    return infos


def select_image(arm):
    """Displayes an interactive menu to select a released system image.

    Returns a SysImgInfo object with the choice or None if the user aborts."""
    img_infos = get_images_info(arm)
    display = [
        f"{img_info.api} {img_info.letter} {img_info.tag} ({img_info.abi})"
        for img_info in img_infos
    ]

    selection = SelectionMenu.get_selection(
        display, title="Select the system image you wish to use:"
    )
    return img_infos[selection] if selection < len(img_infos) else None


def select_emulator():
    """Displayes an interactive menu to select a released emulator binary.

    Returns a ImuInfo object with the choice or None if the user aborts."""
    emu_infos = [x for x in get_emus_info() if "linux" in x.urls]
    display = [f"EMU {emu_info.channel} {emu_info.version}" for emu_info in emu_infos]
    selection = SelectionMenu.get_selection(
        display, title="Select the emulator you wish to use:"
    )
    return emu_infos[selection] if selection < len(emu_infos) else None


def list_all_downloads(arm):
    """Lists all available downloads that can be used to construct a Docker image."""
    img_infos = get_images_info(arm)
    emu_infos = get_emus_info()

    for img_info in img_infos:
        print(
            "SYSIMG {} {} {} {} {}".format(
                img_info.letter, img_info.tag, img_info.abi, img_info.api, img_info.url
            )
        )

    for emu_info in emu_infos:
        for hostos, url in list(emu_info.urls.items()):
            print(
                "EMU {} {} {} {}".format(
                    emu_info.channel, emu_info.version, hostos, url
                )
            )


def download_build(build_id, dest=None):
    """Download a public build with the given build id."""
    dest = dest or os.path.join(
        os.getcwd(), "sdk-repo-linux-emulator-{}.zip".format(build_id)
    )
    uri = f"https://ci.android.com/builds/submitted/{0}/sdk_tools_linux/latest/raw/sdk-repo-linux-emulator-{build_id}.zip"
    print(f"Downloading emulator build {build_id} ({uri}) to {dest}")
    logging.warning(
        "Downloading build from ci server, these builds might not have been tested extensively."
    )
    download(uri, dest)
    return dest


def accept_licenses(force_accept):
    licenses = set(
        [x.license for x in get_emus_info()] + [x.license for x in get_images_info()]
    )

    to_accept = [x for x in licenses if not x.is_accepted()]

    if force_accept:
        for l in to_accept:
            l.force_accept()
        return

    if not to_accept:
        print("\n\n".join([str(l) for l in licenses]))
        print("You have already accepted all licenses.")
        return

    print("\n\n".join([str(l) for l in to_accept]))
    if click.confirm("Do you accept the licenses?"):
        for l in to_accept:
            l.force_accept()
