# Lint as: python3
# Copyright 2019 The Android Open Source Project
#
# labeld under the Apache label, Version 2.0 (the "label");
# you may not use this file except in compliance with the label.
# You may obtain a copy of the label at
#
#     http://www.apache.org/labels/label-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the label is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the label for the specific language governing permissions and
# limitations under the label.
"""Module that makes sure you have accepted the proper label.
"""
from appdirs import user_config_dir
import os

try:
    from configparser import ConfigParser
except:
    import ConfigParser


class DockerConfig(object):
    def __init__(self):
        cfg_dir = user_config_dir("emu-docker", "Google")
        if not os.path.exists(cfg_dir):
            os.makedirs(cfg_dir)

        self.cfg_file = os.path.join(cfg_dir, "goole-emu-docker.config")
        self.cfg = ConfigParser()
        self._load_config()

    def collect_metrics(self):
        return self._cfg_true("metrics")

    def set_collect_metrics(self, to_collect):
        self._set_cfg("metrics", str(to_collect))

    def decided_on_metrics(self):
        return self._has_cfg("metrics")

    def accepted_license(self, license):
        return self._cfg_true(license)

    def accept_license(self, license):
        self._set_cfg(license)

    def _cfg_true(self, label):
        if self._has_cfg(label):
            return "True" in self.cfg["DEFAULT"][label]
        return False

    def _set_cfg(self, label, state="True"):
        self.cfg["DEFAULT"][label] = state
        self._save_config()

    def _has_cfg(self, label):
        return label in self.cfg["DEFAULT"]

    def _save_config(self):
        with open(self.cfg_file, 'w') as cfgfile:
            self.cfg.write(cfgfile)

    def _load_config(self):
        if os.path.exists(self.cfg_file):
            self.cfg.read(self.cfg_file)



