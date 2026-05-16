# Copyright 2026 The Android Open Source Project
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
"""Tests for DockerContainer helpers that don't need a real docker daemon."""
import unittest.mock as mock

import pytest

from emu.containers.docker_container import DockerContainer


class _NamedContainer(DockerContainer):
    """Minimal DockerContainer subclass for testing the base-class lookups."""

    def __init__(self, name, repo=None):
        super().__init__(repo)
        self._name = name

    def image_name(self):
        return self._name

    def docker_tag(self):
        return "latest"

    def write(self, dest):  # abstract no-op for the test
        pass


def _img(*tags):
    """Build a minimal stand-in for a docker.models.images.Image."""
    m = mock.Mock()
    m.tags = list(tags)
    return m


@pytest.fixture
def fake_client(monkeypatch):
    """Patch docker.from_env so DockerContainer.get_client() returns our stub."""
    client = mock.Mock()
    monkeypatch.setattr(
        "emu.containers.docker_container.docker.from_env", lambda: client
    )
    return client


# --------------------------------------------------------------------------- #
# docker_image() — exact-name matching, no substring traps
# --------------------------------------------------------------------------- #


def test_docker_image_matches_bare_name(fake_client):
    target = _img("36-google-x64:latest")
    fake_client.images.list.return_value = [target]

    c = _NamedContainer("36-google-x64")
    assert c.docker_image() is target


def test_docker_image_matches_repo_qualified_name(fake_client):
    target = _img("us-docker.pkg.dev/android-emulator-268719/images/36-google-x64:latest")
    fake_client.images.list.return_value = [target]

    c = _NamedContainer("36-google-x64")
    assert c.docker_image() is target


def test_docker_image_does_not_match_sys_prefix(fake_client):
    """The sys-img layer's tag must not satisfy a lookup for the emulator layer."""
    sys_img = _img("sys-36-google-x64:latest")
    fake_client.images.list.return_value = [sys_img]

    c = _NamedContainer("36-google-x64")
    assert c.docker_image() is None


def test_docker_image_does_not_match_suffix(fake_client):
    """A tag with a suffix appended to the target name must not satisfy a bare-name lookup."""
    suffixed = _img("36-google-x64-foo:latest")
    fake_client.images.list.return_value = [suffixed]

    c = _NamedContainer("36-google-x64")
    assert c.docker_image() is None


def test_docker_image_picks_exact_among_distractors(fake_client):
    """With several near-matches present, only the exact one is returned."""
    sys_img = _img("sys-36-google-x64:latest")
    ps16k = _img("36-google-x64-ps16k:latest")
    target = _img("36-google-x64:latest")
    # exact match is intentionally last in the list to defeat first-hit-wins
    fake_client.images.list.return_value = [sys_img, ps16k, target]

    c = _NamedContainer("36-google-x64")
    assert c.docker_image() is target


def test_docker_image_returns_none_when_no_images(fake_client):
    fake_client.images.list.return_value = []

    c = _NamedContainer("36-google-x64")
    assert c.docker_image() is None


def test_docker_image_skips_untagged_image(fake_client):
    untagged = _img()  # img.tags == []
    target = _img("36-google-x64:latest")
    fake_client.images.list.return_value = [untagged, target]

    c = _NamedContainer("36-google-x64")
    assert c.docker_image() is target
