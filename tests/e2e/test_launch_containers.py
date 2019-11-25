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
"""End 2 end test that builds every image.

   This is super expensive..
"""

import collections
import itertools
import sys
import subprocess

import docker
import pytest
import unittest

import emu.emu_docker as emu_docker
import emu.docker_device as device
import emu.emu_downloads_menu as menu
from utils import TempDir, find_adb, find_free_port



Arguments = collections.namedtuple("Args", "emuzip, imgzip, dest, tag, start, extra")

@pytest.mark.slow
@pytest.mark.e2e
@pytest.mark.parametrize('channel, img', [('canary', 'Q'), ('stable', 'P')])
def test_build_container(channel, img):
    assert docker.from_env().ping()
    with TempDir() as tmp:
        args = Arguments(channel, img, tmp, None, False, "")
        device = emu_docker.create_docker_image(args)
        assert device.identity is not None
        client = docker.from_env()
        assert client.images.get(device.identity) is not None

@pytest.mark.slow
@pytest.mark.e2e
@pytest.mark.linux
@pytest.mark.parametrize('channel, img', [('canary', 'Q'), ('stable', 'P')])
def test_run_container(channel, img):
    assert docker.from_env().ping()
    with TempDir() as tmp:
        args = Arguments(channel, img, tmp, None, False, "")
        device = emu_docker.create_docker_image(args)
        port = find_free_port()

        # Launch this thing.
        device.launch(device.identity, port)
        # Now we are going to insepct this thing.
        api_client = device.get_api_client()
        status = api_client.inspect_container(device.container.id)
        state = status["State"]
        assert state["Status"] == "running"

        # Acceptable states:
        # starting --> We are still launching
        # healthy --> Yay, we booted! Good to go..
        health = state["Health"]["Status"]
        while health == "starting":
            health = api_client.inspect_container(device.container.id)["State"]["Health"]["Status"]

        assert health == "healthy"

        # Good, good.. From an internal perspective things look great.
        # Can we connect with adb from outside the container?
        adb = find_adb()

        # Erase knowledge of existing devices.
        subprocess.check_output([adb, "kill-server"])
        name = "localhost:{}".format(port)
        subprocess.check_output([adb, "connect", name])

        # Boot complete should be true..
        res = subprocess.check_output([adb, "-s", name, "shell", "getprop", "dev.bootcomplete"])
        assert "1" in str(res)

        api_client.stop(device.container.id)
