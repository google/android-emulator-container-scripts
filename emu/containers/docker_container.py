import abc
import logging
import os
import re
import shutil
from pathlib import Path
from typing import Optional

import docker
from docker.models.images import Image

from emu.containers.progress_tracker import ProgressTracker


class DockerContainer:
    """A Docker Device is capable of creating and launching docker images.

    In order to successfully create and launch a docker image you must either
    run this as root, or have enabled sudoless docker.
    """

    TAG_REGEX: re.Pattern = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9._-]*:?[a-zA-Z0-9._-]*")

    # Update this once arm is really an option.
    DEFAULT_PLATFORM = "linux/amd64"

    def __init__(self, repo: Optional[str] = None):
        if repo and repo[-1] != "/":
            repo += "/"
        self.repo: Optional[str] = repo

    def get_client(self) -> docker.DockerClient:
        return docker.from_env()

    def get_api_client(self) -> docker.APIClient:
        try:
            api_client = docker.APIClient()
            logging.info(api_client.version())
            return api_client
        except Exception as _err:
            logging.exception(
                "Failed to create default client, trying domain socket.", exc_info=True
            )

        api_client = docker.APIClient(base_url="unix://var/run/docker.sock")
        logging.info(api_client.version())
        return api_client

    def push(self) -> None:
        image: str = self.full_name()
        print(
            f"Pushing docker image: {self.full_name()}.. be patient this can take a while!"
        )

        tracker: ProgressTracker = ProgressTracker()
        try:
            client: docker.DockerClient = docker.from_env()
            result = client.images.push(image, "latest", stream=True, decode=True)
            for entry in result:
                tracker.update(entry)
            self.docker_image().tag(f"{self.repo}{self.image_name()}:latest")
        except docker.errors.APIError as err:
            logging.error("Failed to push image due to %s", err, exc_info=True)
            logging.warning("You can manually push the image as follows:")
            logging.warning("docker push %s", image)

    def launch(self, port_map) -> Image:
        """Launches the container with the given sha, publishing abd on port, and gRPC on port 8554

        Returns the container.
        """
        image: Image = self.docker_image()
        client: docker.DockerClient = docker.from_env()
        try:
            container = client.containers.run(
                image=image.id,
                privileged=True,
                publish_all_ports=True,
                detach=True,
                ports=port_map,
            )
            print(f"Launched {container.name} (id:{container.id})")
            print(f"docker logs -f {container.name}")
            print(f"docker stop {container.name}")
            return container
        except Exception as err:
            logging.exception("Unable to run the %s due to %s", image.id, err)
            print("Unable to start the container, try running it as:")
            print(f"./run.sh {image.id}")

    def create_container(self, dest: Path) -> str:
        """Creates the docker container, returning the sha of the container, or None in case of failure."""
        identity = None
        image_tag = self.full_name()
        print(f"docker build {dest} -t {image_tag}")
        try:
            api_client = self.get_api_client()
            logging.info(
                "build(path=%s, tag=%s, rm=True, decode=True)", dest, image_tag
            )
            result = api_client.build(
                path=str(dest.absolute()), tag=image_tag, rm=True, decode=True,
                platform=DockerContainer.DEFAULT_PLATFORM
            )
            for entry in result:
                if "stream" in entry and entry["stream"].strip():
                    logging.info(entry["stream"])
                if "aux" in entry and "ID" in entry["aux"]:
                    identity = entry["aux"]["ID"]
                if "error" in entry:
                    logging.error(entry["error"])
            client = docker.from_env()
            image = client.images.get(identity)
            image.tag(self.repo + self.image_name(), "latest")
        except docker.errors.APIError as err:
            logging.error("Failed to create container due to %s.", err, exc_info=True)
            logging.warning("You can manually create the container as follows:")
            logging.warning("docker build -t %s %s", image_tag, dest)

        return identity

    def clean(self, dest: Path) -> None:
        if dest.exists():
            shutil.rmtree(dest)

        dest.mkdir(parents=True)

    def pull(self) -> Image:
        """Tries to retrieve the given image and tag.

        Return True if succeeded, False when failed.
        """
        client = self.get_api_client()
        try:
            tracker = ProgressTracker()
            result = client.pull(self.repo + self.image_name(), self.docker_tag())
            for entry in result:
                tracker.update(entry)
        except docker.errors.APIError as err:
            logging.debug(
                "Unable to pull image %s%s:%s due to %s",
                self.repo,
                self.image_name(),
                self.docker_tag(),
                err,
            )
            return None

        # We obtained the image, so it should exist.
        return self.docker_image()

    def full_name(self) -> str:
        """Gets the complete name of this image, this can be used in the build step.
        Generally there are two modes:

        - It is available in a remote repository
        - It is available locally
        """
        local = self.docker_image()

        # Available locally, get the first tag
        if local:
            return local.tags[0]

        return ""

    def latest_name(self):
        if self.repo:
            return f"{self.repo}{self.image_name()}:{self.docker_tag()}"
        return (self.image_name(), "latest")

    def create_cloud_build_step(self, dest: Path):
        return {
            "name": "gcr.io/cloud-builders/docker",
            "args": [
                "build",
                "-t",
                self.full_name(),
                "-t",
                self.latest_name(),
                os.path.basename(dest),
            ],
        }

    def docker_image(self) -> Image:
        """The docker local docker image if any

        Returns:
            {docker.models.images.Image}: A docker image object, or None.
        """
        client = self.get_client()
        for img in client.images.list():
            for tag in img.tags:
                if self.image_name() in tag:
                    return img
        return None

    def available(self):
        """True if this container image is locally available."""
        if self.docker_image():
            logging.info("%s is avaliable", self.docker_image().tags)
            return True
        return False

    def build(self, dest: Path):
        logging.info("Building %s in %s", self, dest)
        self.write(Path(dest))
        return self.create_container(Path(dest))

    def can_pull(self):
        """True if this container image can be pulled from a registry."""
        return self.pull() is not None

    @abc.abstractmethod
    def write(self, destination: Path):
        """Method responsible for writing the Dockerfile and all necessary files to build a container.

        Args:
            destination ({string}): A path to a directory where all the container files should reside.

        Raises:
            NotImplementedError: [description]
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def image_name(self):
        """The image name without the tag used to uniquely identify this image.

        Raises:
            NotImplementedError: [description]
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def docker_tag(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def depends_on(self):
        """Name of the system image this container is build on."""
        raise NotImplementedError()

    def __str__(self):
        return self.image_name() + ":" + self.docker_tag()
