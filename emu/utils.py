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
import logging
from pathlib import Path

import requests
from tqdm import tqdm


def download(url, dest : Path) -> Path:
    """Downloads the given url to the given destination with a progress bar.

    This function will immediately return if the file already exists.
    """
    dest = Path(dest)
    if dest.exists():
        print(f"  Skipping already downloaded file: {dest}")
        return dest

    # Make sure destination directory exists.
    if not dest.parent.exists():
        dest.parent.mkdir(parents=True)

    logging.info("Get %s -> %s", url, dest)
    with requests.get(url, timeout=5, stream=True) as r:
        with tqdm(r, total=int(r.headers["content-length"]), unit="B", unit_scale=True) as t:
            with open(dest, "wb") as f:
                for data in r:
                    f.write(data)
                    t.update(len(data))
    return dest
