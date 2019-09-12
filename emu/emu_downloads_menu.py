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

import os
import xml.etree.ElementTree as ET
import zipfile

import urlfetch
from consolemenu import SelectionMenu
from tqdm import tqdm

SYSIMG_REPOS = [
    'https://dl.google.com/android/repository/sys-img/android/sys-img2-1.xml',
    'https://dl.google.com/android/repository/sys-img/google_apis/sys-img2-1.xml',
    'https://dl.google.com/android/repository/sys-img/google_apis_playstore/sys-img2-1.xml'
]

EMU_REPOS = [
    'https://dl.google.com/android/repository/repository2-1.xml',
]

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
}


def _download(url, dest):
    """Downloads the given url to the given destination with a progress bar.

    This function will immediately return if the file already exists.
    """
    if os.path.exists(dest):
        print("  Skipping already downloaded file: {}".format(dest))
        return dest
    with urlfetch.get(url) as r:
        with tqdm(r, total=int(r.headers['content-length']), unit='B', unit_scale=True) as t:
            with open(dest, 'wb') as f:
                for data in r:
                    f.write(data)
                    t.update(len(data))
    return dest


class AndroidReleaseZip(object):
    """Provides information of released android products.

    Every released zip file contains a source.properties file, this
    source.properties file contains [key]=[value] pairs with information
    aobut the contents of the zip.
    """

    def __init__(self, fname):
        self.fname = fname
        if not zipfile.is_zipfile(fname):
            raise "{} is not a zipfile!".format(fname)
        with zipfile.ZipFile(fname, 'r') as sysimg:
            props = [x for x in sysimg.infolist(
            ) if 'source.properties' in x.filename]
            if not props:
                raise "{} does not contain source.properties!".format(fname)
            prop = [str(a) for a in sysimg.read(props[0]).splitlines()]
            self.props = dict([a.split('=') for a in prop if '=' in a])

    def api(self):
        """The api level, if any."""
        return self.props.get('AndroidVersion.ApiLevel', "Unknown Api")

    def abi(self):
        """The abi, of x86 if not found."""
        return self.props.get('SystemImage.Abi', "x86")

    def tag(self):
        """The tag associated with this release."""
        return self.props.get('SystemImage.TagId', "default")

    def desc(self):
        """Descripton of this release."""
        return self.props.get('Pkg.Desc')

    def revision(self):
        """The revision of this release."""
        return self.props.get('Pkg.Revision')


class SysImgInfo(object):
    """Provides information about a released system image."""

    def __init__(self, pkg):
        details = pkg.find('type-details')
        self.api = details.find('api-level').text

        codename = details.find('codename')
        if codename is None:
            if self.api in API_LETTER_MAPPING:
                self.letter = API_LETTER_MAPPING[self.api]
            else:
                self.letter = "_"
        else:
            self.letter = codename.text

        self.tag = details.find('tag').find('id').text

        if self.tag == 'default':
            self.tag = 'android'
        self.abi = details.find('abi').text
        self.zip = pkg.find('.//url').text
        self.url = 'https://dl.google.com/android/repository/sys-img/%s/%s' % (
            self.tag, self.zip)

    def download(self, dest=None):
        dest = dest or os.path.join(
            os.getcwd(), 'sys-img-{}-{}-{}.zip'.format(self.tag, self.api, self.letter))
        print("Downloading system image: {} {} {} {} to {}".format(
            self.tag, self.api, self.letter, self.abi, dest))
        return _download(self.url, dest)


class EmuInfo(object):
    """Provides information about a released emulator."""

    def __init__(self, pkg):
        rev = pkg.find('revision')

        rev_major = rev.find('major').text
        rev_minor = rev.find('minor').text
        rev_micro = rev.find('micro').text

        archives = pkg.find('archives')
        channel = pkg.find('channelRef')

        self.channel = CHANNEL_MAPPING[channel.attrib['ref']]

        self.version = "%s.%s.%s" % (rev_major, rev_minor, rev_micro)
        self.urls = {}

        for archive in archives:
            url = archive.find('.//url').text
            hostos = archive.find('host-os').text
            self.urls[hostos] = "https://dl.google.com/android/repository/%s" % url

    def download(self, hostos, dest=None):
        """"Downloads the released pacakage for the given os to the dest."""
        dest = dest or os.path.join(
            os.getcwd(), 'emulator-{}.zip'.format(self.version))
        print("Downloading emulator: {} {} to {}".format(
            self.channel, self.version, dest))
        return _download(self.urls[hostos], dest)


def get_images_info():
    """Gets all the publicly available system images from the Android Image Repos.

         Returns a list of AndroidSystemImages that were found.
      """
    xml = []
    for url in SYSIMG_REPOS:
        response = urlfetch.get(url)
        if response.status == 200:
            xml.append(response.content)
    xml = [ET.fromstring(x).findall('remotePackage') for x in xml]
    # Flatten the list of lists into a system image objects.
    infos = [SysImgInfo(item) for sublist in xml for item in sublist]
    # Filter only for intel images that we know that work
    x86_64_imgs = [info for info in infos if info.abi ==
                   "x86_64" and info.letter >= "O"]
    x86_imgs = [info for info in infos if info.abi ==
                "x86" and info.letter >= "K"]
    return sorted(x86_64_imgs + x86_imgs, key=lambda x: x.letter)


def get_emus_info():
    """Gets all the publicly available system images from the Android Image Repos.

         Returns a list of AndroidSystemImages that were found.
      """
    xml = []
    for url in EMU_REPOS:
        response = urlfetch.get(url)
        if response.status == 200:
            xml.append(response.content)
    xml = [[p for p in ET.fromstring(x).findall(
        'remotePackage') if "emulator" == p.attrib["path"]] for x in xml]
    # Flatten the list of lists into a system image objects.
    infos = [EmuInfo(item) for sublist in xml for item in sublist]
    return infos


def select_image():
    """Displayes an interactive menu to select a released system image.

    Returns a SysImgInfo object with the choice or None if the user aborts.
    """
    img_infos = get_images_info()
    display = ["{} {} {} ({})".format(img_info.api, img_info.letter,
                                      img_info.tag, img_info.abi) for img_info in img_infos]
    selection = SelectionMenu.get_selection(
        display, title='Select the system image you wish to use:')
    return img_infos[selection] if selection < len(img_infos) else None


def select_emulator():
    """Displayes an interactive menu to select a released emulator binary.

    Returns a ImuInfo object with the choice or None if the user aborts.
    """
    emu_infos = [x for x in get_emus_info() if 'linux' in x.urls]
    display = ["EMU {} {}".format(
        emu_info.channel, emu_info.version) for emu_info in emu_infos]
    selection = SelectionMenu.get_selection(
        display,  title='Select the emulator you wish to use:')
    return emu_infos[selection] if selection < len(emu_infos) else None


def list_all_downloads():
    """Lists all available downloads that can be used to construct a Docker image."""
    img_infos = get_images_info()
    emu_infos = get_emus_info()

    for img_info in img_infos:
        print("SYSIMG {} {} {} {} {}".format(img_info.api,
                                             img_info.letter, img_info.tag, img_info.abi, img_info.url))

    for emu_info in emu_infos:
        for (hostos, url) in list(emu_info.urls.items()):
            print("EMU {} {} {} {}".format(
                emu_info.channel, emu_info.version, hostos, url))
