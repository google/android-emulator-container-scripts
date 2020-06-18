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
import zipfile

import click
import urlfetch
from consolemenu import SelectionMenu
from tqdm import tqdm

from emu.docker_config import DockerConfig

SYSIMG_REPOS = [
    "https://dl.google.com/android/repository/sys-img/android/sys-img2-1.xml",
    "https://dl.google.com/android/repository/sys-img/google_apis/sys-img2-1.xml",
    "https://dl.google.com/android/repository/sys-img/google_apis_playstore/sys-img2-1.xml",
]

EMU_REPOS = ["https://dl.google.com/android/repository/repository2-1.xml"]

CHANNEL_MAPPING = {"channel-0": "stable", "channel-1": "beta", "channel-2": "dev", "channel-3": "canary"}

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
}

# Older versions might not work as expected.
MIN_REL_I386 = "K"
MIN_REL_X64 = "O"


# Platform tools, needed to get adb.
PLATFORM_TOOLS_URL = "https://dl.google.com/android/repository/platform-tools_r29.0.5-linux.zip"


def _download(url, dest):
    """Downloads the given url to the given destination with a progress bar.

    This function will immediately return if the file already exists.
    """
    if os.path.exists(dest):
        print("  Skipping already downloaded file: {}".format(dest))
        return dest
    with urlfetch.get(url) as r:
        with tqdm(r, total=int(r.headers["content-length"]), unit="B", unit_scale=True) as t:
            with open(dest, "wb") as f:
                for data in r:
                    f.write(data)
                    t.update(len(data))
    return dest


class AndroidReleaseZip(object):
    """Provides information of released android products.

    Every released zip file contains a source.properties file, this
    source.properties file contains [key]=[value] pairs with information
    about the contents of the zip.
    """

    ABI_CPU_MAP = {"armeabi-v7a": "arm", "arm64-v8a": "arm64", "x86_64": "x86_64", "x86": "x86"}
    SHORT_MAP = {"armeabi-v7a": "a32", "arm64-v8a": "a64", "x86_64": "x64", "x86": "x86"}
    SHORT_TAG = {"android": "aosp", "google_apis": "google", "google_apis_playstore": "playstore"}

    def __init__(self, fname):
        self.fname = fname
        if not zipfile.is_zipfile(fname):
            raise Exception("{} is not a zipfile!".format(fname))
        with zipfile.ZipFile(fname, "r") as sysimg:
            props = [x for x in sysimg.infolist() if "source.properties" in x.filename]
            if not props:
                raise Exception("{} does not contain source.properties!".format(fname))
            prop = sysimg.read(props[0]).decode("utf-8").splitlines()
            self.props = dict([a.split("=") for a in prop if "=" in a])

    def __str__(self):
        return "{}-{}".format(self.desc(), self.revision())

    def api(self):
        """The api level, if any."""
        return self.props.get("AndroidVersion.ApiLevel", "")

    def codename(self):
        """First letter of the desert, if any."""
        if 'AndroidVersion.CodeName' in self.props:
            return self.props['AndroidVersion.CodeName']
        api = self.api()
        if api in API_LETTER_MAPPING:
            return API_LETTER_MAPPING[api]
        else:
            return "_"

    def abi(self):
        """The abi if any."""
        return self.props.get("SystemImage.Abi", "")

    def short_abi(self):
        if self.abi() not in self.SHORT_MAP:
            logging.error("%s not in short map", self)
        return self.SHORT_MAP[self.abi()]

    def cpu(self):
        """Returns the cpu architecture, derived from the abi."""
        return self.ABI_CPU_MAP[self.abi()]

    def gpu(self):
        """Returns whether or not the system has gpu support."""
        return self.props.get("SystemImage.GpuSupport")

    def tag(self):
        """The tag associated with this release."""
        tag = self.props.get("SystemImage.TagId", "")
        if tag == "default" or tag.strip() == "":
            tag = "android"
        return tag

    def short_tag(self):
        return self.SHORT_TAG[self.tag()]

    def desc(self):
        """Descripton of this release."""
        return self.props.get("Pkg.Desc")

    def revision(self):
        """The revision of this release."""
        return self.props.get("Pkg.Revision")

    def build_id(self):
        """The build id, or revision of build id is not available."""
        if "Pgk.BuildId" in self.props:
            return self.props.get("Pkg.BuildId")
        return self.revision()

    def repo_friendly_name(self):
        return "{}-{}-{}".format(self.codename().lower(), self.short_tag(), self.short_abi())

    def is_system_image(self):
        return "System Image" in self.desc()

    def is_emulator(self):
        return "Android Emulator" in self.desc()

    def logger_flags(self):
        if "arm" in self.cpu():
            return "-logcat *:V -show-kernel"
        else:
            return "-shell-serial file:/tmp/android-unknown/kernel.log -logcat-output /tmp/android-unknown/logcat.log"


class PlatformTools(object):
    """The platform tools zip file. It will be downloaded on demand."""

    def __init__(self, fname=None):
        self.platform = fname

    def extract_adb(self, dest):
        if not self.platform:
            self.platform = self.download()
        with zipfile.ZipFile(self.platform, "r") as plzip:
            plzip.extract("platform-tools/adb", dest)

    def download(self, dest=None):
        dest = dest or os.path.join(os.getcwd(), "platform-tools-latest-linux.zip")
        print("Downloading platform tools to {}".format(dest))
        return _download(PLATFORM_TOOLS_URL, dest)


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
        """"Downloads the released pacakage forto the dest."""
        if self.license.accept():
            return _download(url, dest)


class SysImgInfo(LicensedObject):
    """Provides information about a released system image."""

    def __init__(self, pkg, licenses):
        super(SysImgInfo, self).__init__(pkg, licenses)
        details = pkg.find("type-details")
        self.api = details.find("api-level").text

        codename = details.find("codename")
        if codename is None:
            if self.api in API_LETTER_MAPPING:
                self.letter = API_LETTER_MAPPING[self.api]
            else:
                self.letter = "A" # A indicates unknown code.
        else:
            self.letter = codename.text

        self.tag = details.find("tag").find("id").text

        if self.tag == "default":
            self.tag = "android"
        self.abi = details.find("abi").text
        self.zip = pkg.find(".//url").text
        self.url = "https://dl.google.com/android/repository/sys-img/%s/%s" % (self.tag, self.zip)

    def download(self, dest=None):
        dest = dest or os.path.join(
            os.getcwd(), "sys-img-{}-{}-{}-{}.zip".format(self.tag, self.api, self.letter, self.abi)
        )
        print("Downloading system image: {} {} {} {} to {}".format(self.tag, self.api, self.letter, self.abi, dest))
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

    def download(self, hostos="linux", dest=None):
        """"Downloads the released pacakage for the given os to the dest."""
        dest = dest or os.path.join(os.getcwd(), "emulator-{}.zip".format(self.version))
        print("Downloading emulator: {} {} to {}".format(self.channel, self.version, dest))
        return super(EmuInfo, self).download(self.urls[hostos], dest)

    def __str__(self):
        return "{} {}".format(self.channel, self.version)


def get_images_info(arm=False):
    """Gets all the publicly available system images from the Android Image Repos.

    Returns a list of AndroidSystemImages that were found and (hopefully) can boot."""
    xml = []
    for url in SYSIMG_REPOS:
        response = urlfetch.get(url)
        if response.status == 200:
            xml.append(response.content)

    licenses = [License(p) for x in xml for p in ET.fromstring(x).findall("license")]
    licenses = dict([(x.name, x) for x in [y for y in licenses]])

    xml = [ET.fromstring(x).findall("remotePackage") for x in xml]
    # Flatten the list of lists into a system image objects.
    infos = [SysImgInfo(item, licenses) for sublist in xml for item in sublist]
    # Filter only for intel images that we know that work
    x86_64_imgs = [info for info in infos if info.abi == "x86_64" and info.letter >= MIN_REL_X64]
    x86_imgs = [info for info in infos if info.abi == "x86" and info.letter >= MIN_REL_I386]
    slow = []
    if arm:
        slow = [info for info in infos if info.abi.startswith("arm")]
    all_imgs = sorted(x86_64_imgs + x86_imgs + slow, key=lambda x: x.api + x.tag)
    # Filter out windows/darwin images.
    return [i for i in all_imgs if "windows" not in i.url and "darwin" not in i.url]


def find_image(regexpr):
    reg = re.compile(regexpr)
    all_images = get_images_info(True)
    matches = [img for img in all_images if reg.match(str(img))]
    logging.info(
        "Found %s matching images: %s from %s", regexpr, [str(x) for x in matches], [str(x) for x in all_images]
    )
    if not matches:
        raise Exception(
            "No system image found matching {}. Run the list command to list available images".format(regexpr)
        )
    return matches


def find_emulator(channel):
    """Displayes an interactive menu to select a released emulator binary.

    Returns a ImuInfo object with the choice or None if the user aborts.    """
    emu_infos = [x for x in get_emus_info() if "linux" in x.urls and (channel == "all" or x.channel == channel)]
    logging.info("Found %s matching images: %s", channel, [str(x) for x in emu_infos])
    if not emu_infos:
        raise Exception("No emulator found in channel {}".format(channel))
    return emu_infos


def get_emus_info():
    """Gets all the publicly available emulator builds.

         Returns a list of EmuInfo items that were found.    """
    xml = []
    for url in EMU_REPOS:
        response = urlfetch.get(url)
        if response.status == 200:
            xml.append(response.content)

    licenses = [License(p) for x in xml for p in ET.fromstring(x).findall("license")]
    licenses = dict([(x.name, x) for x in [y for y in licenses]])
    xml = [[p for p in ET.fromstring(x).findall("remotePackage") if "emulator" == p.attrib["path"]] for x in xml]
    # Flatten the list of lists into a system image objects.
    infos = [EmuInfo(item, licenses) for sublist in xml for item in sublist]
    return infos


def select_image(arm):
    """Displayes an interactive menu to select a released system image.

    Returns a SysImgInfo object with the choice or None if the user aborts.    """
    img_infos = get_images_info(arm)
    display = [
        "{} {} {} ({})".format(img_info.api, img_info.letter, img_info.tag, img_info.abi) for img_info in img_infos
    ]
    selection = SelectionMenu.get_selection(display, title="Select the system image you wish to use:")
    return img_infos[selection] if selection < len(img_infos) else None


def select_emulator():
    """Displayes an interactive menu to select a released emulator binary.

    Returns a ImuInfo object with the choice or None if the user aborts.    """
    emu_infos = [x for x in get_emus_info() if "linux" in x.urls]
    display = ["EMU {} {}".format(emu_info.channel, emu_info.version) for emu_info in emu_infos]
    selection = SelectionMenu.get_selection(display, title="Select the emulator you wish to use:")
    return emu_infos[selection] if selection < len(emu_infos) else None


def list_all_downloads(arm):
    """Lists all available downloads that can be used to construct a Docker image."""
    img_infos = get_images_info(arm)
    emu_infos = get_emus_info()

    for img_info in img_infos:
        print("SYSIMG {} {} {} {} {}".format(img_info.letter, img_info.tag, img_info.abi, img_info.api, img_info.url))

    for emu_info in emu_infos:
        for (hostos, url) in list(emu_info.urls.items()):
            print("EMU {} {} {} {}".format(emu_info.channel, emu_info.version, hostos, url))
