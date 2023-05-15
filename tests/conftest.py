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
import pytest
import docker
import tempfile
import shutil
from pathlib import Path

@pytest.fixture
def client() -> docker.DockerClient:
    assert docker.from_env().ping()
    yield docker.from_env()


@pytest.fixture
def clean_docker(client):
    # Remove all containers
    containers = client.containers.list(all=True)
    for container in containers:
        container.remove(force=True)

    # Remove all images
    images = client.images.list(all=True)
    for image in images:
        client.images.remove(image.id, force=True)

    yield client

@pytest.fixture()
def temp_dir():
  """Creates a temporary directory that gets deleted after the test."""
  temp_directory = tempfile.mkdtemp()
  yield  Path(temp_directory)
  shutil.rmtree(temp_directory)