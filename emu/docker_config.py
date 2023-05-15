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
"""Module that makes sure you have accepted the proper license.
"""
from configparser import ConfigParser
from pathlib import Path
from typing import Union

from appdirs import user_config_dir


class DockerConfig:
    """Class for managing Docker configuration."""

    def __init__(self):
        """Initialize DockerConfig object."""
        cfg_dir: Path = Path(user_config_dir("emu-docker", "Google"))
        if not cfg_dir.exists():
            cfg_dir.mkdir(parents=True)

        self.cfg_file: Path = cfg_dir / "goole-emu-docker.config"
        self.cfg: ConfigParser = ConfigParser()
        self._load_config()

    def collect_metrics(self) -> bool:
        """Check if the user is okay with collecting metrics.

        Returns:
            bool: True if the user is okay with collecting metrics, False otherwise.
        """
        return self._cfg_true("metrics")

    def set_collect_metrics(self, to_collect: bool):
        """Set whether to collect metrics.

        Args:
            to_collect (bool): True to collect metrics, False otherwise.
        """
        self._set_cfg("metrics", str(to_collect))

    def decided_on_metrics(self) -> bool:
        """Check if the user has made a choice around metrics collection.

        Returns:
            bool: True if the user has made a choice, False otherwise.
        """
        return self._has_cfg("metrics")

    def accepted_license(self, agreement: str) -> bool:
        """Check if the user has accepted the given license agreement.

        Args:
            agreement (str): The license agreement to check.

        Returns:
            bool: True if the user has accepted the license agreement, False otherwise.
        """
        return self._cfg_true(agreement)

    def accept_license(self, agreement: str):
        """Accept the given license agreement.

        Args:
            agreement (str): The license agreement to accept.
        """
        self._set_cfg(agreement)

    def _cfg_true(self, label: str) -> bool:
        """Check if the specified label is true in the configuration.

        Args:
            label (str): The label to check.

        Returns:
            bool: True if the label is set to True in the configuration, False otherwise.
        """
        if self._has_cfg(label):
            return "True" in self.cfg["DEFAULT"][label]
        return False

    def _set_cfg(self, label: str, state: str = "True"):
        """Set the specified label in the configuration.

        Args:
            label (str): The label to set.
            state (str, optional): The state to set (default is "True").
        """
        self._load_config()
        self.cfg["DEFAULT"][label] = state
        self._save_config()

    def _has_cfg(self, label: str) -> bool:
        """Check if the specified label exists in the configuration.

        Args:
            label (str): The label to check.

        Returns:
            bool: True if the label exists in the configuration, False otherwise.
        """
        return label in self.cfg["DEFAULT"]

    def _save_config(self):
        """Save the configuration to the config file."""
        with open(self.cfg_file, "w", encoding="utf-8") as cfgfile:
            self.cfg.write(cfgfile)

    def _load_config(self):
        """Load the configuration from the config file if it exists."""
        if self.cfg_file.exists():
            self.cfg.read(self.cfg_file)
