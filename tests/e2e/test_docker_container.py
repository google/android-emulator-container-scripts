# Copyright 2023 The Android Open Source Project
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
"""Test that some remote containers are available."""
import pytest
from emu.emu_downloads_menu import find_image
from emu.containers.system_image_container import SystemImageContainer


@pytest.mark.e2e
@pytest.mark.parametrize(
    "image",
    [
        "P google_apis x86_64",
        "P android x86_64",
        #  "Q google_apis x86_64",
        "Q android x86_64",
        "R google_apis x86_64",
        # "R android x86_64",
    ],
)
def test_can_pull(image):
    """Make sure we have this set of images publicly available."""
    info = find_image(image)[0]
    assert info

    container = SystemImageContainer(info)
    assert container.can_pull()


@pytest.mark.e2e
@pytest.mark.parametrize(
    "image",
    [
        "K android x86",
    ],
)
def test_can_build(image, temp_dir):
    """Make sure we can build images that are not available."""
    info = find_image(image)[0]
    assert info

    # We should not be hosting this image
    container = SystemImageContainer(info)
    assert not container.can_pull()

    # But we should be able to build it
    assert container.build(temp_dir)

    # And now it should be available locally
    assert container.available()


