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
from tqdm import tqdm


class ProgressTracker:
    """
    A class that tracks progress using tqdm for a set of layers that are pushed.
    """

    def __init__(self):
        """        Initializes a new instance of ProgressTracker with an empty progress dictionary.        """
        self.progress = {}

    def __del__(self):
        """        Closes the tqdm progress bars for all entries in the progress dictionary.        """
        for _key, value in self.progress.items():
            value["tqdm"].close()

    def update(self, entry):
        """Updates the progress bars given an entry dictionary."""
        if "id" not in entry:
            return

        identity = entry["id"]
        if identity not in self.progress:
            self.progress[identity] = {
                "tqdm": tqdm(total=0, unit="B", unit_scale=True),  # The progress bar
                "total": 0,  # Total of bytes we are shipping
                "status": "",  # Status message.
                "current": 0,  # Current of total already send.
            }

        prog = self.progress[identity]
        total = int(entry.get("progressDetail", {}).get("total", -1))
        current = int(entry.get("progressDetail", {}).get("current", 0))

        if prog["total"] != total and total != -1:
            prog["total"] = total
            prog["tqdm"].reset(total=total)

        if prog["status"] != entry["status"]:
            prog["status"] = entry["status"]
            prog["tqdm"].set_description(f"{entry.get('status')} {identity}")

        if current != 0:
            diff = current - prog["current"]
            prog["current"] = current
            prog["tqdm"].update(diff)
