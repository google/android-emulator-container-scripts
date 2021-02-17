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

import os
import logging
from tqdm import tqdm
import requests


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


def mkdir_p(path):
    """Make directories recursively if path not exists."""
    if not os.path.exists(path):
        os.makedirs(path)


def download(url, dest):
    """Downloads the given url to the given destination with a progress bar.

    This function will immediately return if the file already exists.
    """
    if os.path.exists(dest):
        print("  Skipping already downloaded file: {}".format(dest))
        return dest
    mkdir_p(os.path.dirname(dest))
    logging.info("Get %s -> %s", url, dest)
    with requests.get(url, timeout=5, stream=True) as r:
        with tqdm(r, total=int(r.headers["content-length"]), unit="B", unit_scale=True) as t:
            with open(dest, "wb") as f:
                for data in r:
                    f.write(data)
                    t.update(len(data))
    return dest


def api_codename(api):
    """First letter of the desert, if any."""
    if api in API_LETTER_MAPPING:
        return API_LETTER_MAPPING[api]
    else:
        return "_"
