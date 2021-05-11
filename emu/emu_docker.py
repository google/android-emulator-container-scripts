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

"""Minimal dependency script to create a Dockerfile for a particular combination of emulator and system image."""

import argparse
import itertools
import logging
import os
import sys
import re

import click
import colorlog

import emu
import emu.emu_downloads_menu as emu_downloads_menu
from emu.docker_config import DockerConfig
from emu.cloud_build import cloud_build
from emu.containers.emulator_container import EmulatorContainer
from emu.containers.system_image_container import SystemImageContainer


def list_images(args):
    """Lists all the publicly available system and emlator images."""
    emu_downloads_menu.list_all_downloads(args.arm)


def accept_licenses(args):
    emu_downloads_menu.accept_licenses(args.accept)


def create_cloud_build_distribuition(args):
    cloud_build(args)


def metrics_config(args):
    cfg = DockerConfig()
    if args.metrics:
        cfg.set_collect_metrics(True)
    if args.no_metrics:
        cfg.set_collect_metrics(False)

    if not cfg.decided_on_metrics():
        logging.warning(
            "Please opt in or out of metrics collection.\n"
            "You will receive this warning until an option is selected.\n"
            "To opt in or out pass the --metrics or --no-metrics flag\n"
            "Note, that metrics will only be collected if you opt in."
        )
    return cfg


def create_docker_image(args):
    """Create a directory containing all the necessary ingredients to construct a docker image.

    Returns the created DockerDevice objects.
    """
    cfg = metrics_config(args)
    imgzip = [args.imgzip]
    if not os.path.exists(imgzip[0]):
        imgzip = emu_downloads_menu.find_image(imgzip[0])

    emuzip = [args.emuzip]
    if emuzip[0] in ["stable", "canary", "all"]:
        emuzip = [x.download() for x in emu_downloads_menu.find_emulator(emuzip[0])]
    elif re.match(r"\d+", emuzip[0]):
        # We must be looking for a build id
        logging.info("Treating %s as a build id", emuzip[0])
        emuzip = [emu_downloads_menu.download_build(emuzip[0])]

    devices = []
    logging.info("Using repo %s", args.repo)
    for (img, emu) in itertools.product(imgzip, emuzip):
        logging.info("Processing %s, %s", img, emu)
        sys_docker = SystemImageContainer(img, args.repo)
        if not sys_docker.available() and not sys_docker.can_pull():
            sys_docker.build(args.dest)
        else:
            print("No need to build {}, it's already available".format(sys_docker))
        if args.push:
            sys_docker.push()

        if args.sys:
            continue

        emu_docker = EmulatorContainer(emu, sys_docker, args.repo, cfg.collect_metrics(), args.extra)
        emu_docker.build(args.dest)

        if args.start:
            emu_docker.launch({"5555/tcp": 5555, "8554/tcp": 8554})
        if args.push:
            emu_docker.push()

        devices.append(emu_docker)

    return devices


def create_docker_image_interactive(args):
    """Interactively create a docker image by selecting the desired combination from a menu."""
    img = emu_downloads_menu.select_image(args.arm) or sys.exit(1)
    emulator = emu_downloads_menu.select_emulator() or sys.exit(1)
    cfg = DockerConfig()
    metrics = False

    if not cfg.decided_on_metrics():
        cfg.set_collect_metrics(
            click.confirm(
                "Would you like to help make the emulator better by sending usage statistics to Google upon (graceful) emulator exit?"
            )
        )
    metrics = cfg.collect_metrics()

    emu_zip = emulator.download("linux")
    logging.info("Processing %s, %s", img, emu)
    sys_docker = SystemImageContainer(img, args.repo)
    if not sys_docker.available() and not sys_docker.can_pull():
        sys_docker.build(args.dest)

    emu_docker = EmulatorContainer(emu_zip, sys_docker, args.repo, metrics)
    emu_docker.build(args.dest)

    if args.start:
        emu_docker.launch({"5555/tcp": 5555, "8554/tcp": 8554})


def main():
    """Entry point that parses the argument, and invokes the proper functions."""

    parser = argparse.ArgumentParser(
        description="List and create emulator docker containers ({}).".format(emu.__version__),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-v", "--verbose", dest="verbose", action="store_true", help="Set verbose logging")

    subparsers = parser.add_subparsers()

    list_parser = subparsers.add_parser(
        "list", help="list all the available the publicly available emulators and system images."
    )

    list_parser.add_argument(
        "--arm",
        action="store_true",
        help="Display arm images. Note that arm images are not hardware accelerated and are *extremely* slow.",
    )
    list_parser.set_defaults(func=list_images)

    license_parser = subparsers.add_parser(
        "licenses", help="Lists all licenses and gives you a chance to accept or reject them."
    )
    license_parser.add_argument("--accept", action="store_true", help="Accept all licensens after displaying them.")
    license_parser.set_defaults(func=accept_licenses)

    create_parser = subparsers.add_parser(
        "create",
        help="Given an emulator and system image zip file, "
        "generates a Docker image comprising complete environment in which the Android Emulator runs. "
        "After the Docker image is started up, interaction with the emulator is made possible via port forwarding and ADB, "
        "or gRPC and WebRTC.",
    )
    create_parser.add_argument(
        "emuzip",
        help="Zipfile containing the a publicly released emulator, or (canary|stable|[0-9]+) to use the latest canary, stable, or build id of the emulator to use. "
        "Keep in mind that using a build id can result in downloading an untested pre-release emulator build from the android ci server.",
    )
    create_parser.add_argument(
        "imgzip",
        help="Zipfile containing a public system image that should be launched, or a regexp matching the image to retrieve. "
        "All the matching images will be selected when using a regex. "
        'Use the list command to show all available images. For example "P google_apis_playstore x86_64".',
    )
    create_parser.add_argument(
        "--extra",
        default="",
        help="Series of additional commands to pass on to the emulator. This *MUST* be the last parameter. "
        "For example: --extra -http-proxy http://example.google.com",
        nargs=argparse.REMAINDER,
    )
    create_parser.add_argument(
        "--dest", default=os.path.join(os.getcwd(), "src"), help="Destination for the generated docker files"
    )
    create_parser.add_argument("--tag", default="", help="Docker tag, defaults to the emulator build id")
    create_parser.add_argument(
        "--repo",
        default="us-docker.pkg.dev/android-emulator-268719/images",
        help="Repo prefix, for example: us.gcr.io/emu-dev/",
    )
    create_parser.add_argument(
        "--push",
        action="store_true",
        help="Push the created image to your repository, as marked by the --repo argument.",
    )
    create_parser.add_argument(
        "--gpu", action="store_true", help="Build an image with gpu drivers, providing hardware acceleration"
    )

    create_parser.add_argument(
        "--metrics",
        action="store_true",
        help="When enabled, the emulator will send usage metrics to Google when the container exists gracefully.",
    )
    create_parser.add_argument("--no-metrics", action="store_true", help="Disables the collection of usage metrics.")
    create_parser.add_argument(
        "--start",
        action="store_true",
        help="Starts the container after creating it. "
        "All exposed ports are forwarded, and your private adbkey (if available) is injected but not stored.",
    )
    create_parser.add_argument("--sys", action="store_true", help="Process system image layer only.")
    create_parser.set_defaults(func=create_docker_image)

    create_inter = subparsers.add_parser(
        "interactive",
        help="Interactively select which system image and emulator binary to use when creating a docker container",
    )
    create_inter.add_argument(
        "--extra",
        default="",
        help="Series of additional commands to pass on to the emulator. "
        'For example -turncfg \\"curl -s -X POST https://networktraversal.googleapis.com/v1alpha/iceconfig?key=MySec\\"',
    )
    create_inter.add_argument(
        "--dest", default=os.path.join(os.getcwd(), "src"), help="Destination for the generated docker files"
    )
    create_inter.add_argument(
        "--gpu", action="store_true", help="Build an image with gpu drivers, providing hardware acceleration"
    )
    create_inter.add_argument(
        "--start",
        action="store_true",
        help="Starts the container after creating it. "
        "All exposed ports are forwarded, and your private adbkey (if available) is injected but not stored.",
    )
    create_inter.add_argument(
        "--arm",
        action="store_true",
        help="Display arm images. Note that arm images are not hardware accelerated and are *extremely* slow.",
    )
    create_inter.add_argument(
        "--repo",
        default="us-docker.pkg.dev/android-emulator-268719/images",
        help="Repo prefix, for example: us.gcr.io/emu-dev/",
    )
    create_inter.set_defaults(func=create_docker_image_interactive)

    dist_parser = subparsers.add_parser(
        "cloud-build",
        help="Create a cloud builder distribution. This will create a distribution for publishing container images to a GCE repository."
        "This is likely only useful if you are within Google.",
    )
    dist_parser.add_argument(
        "--repo",
        default="us-docker.pkg.dev/android-emulator-268719/images",
        help="Repo prefix, for example: us.gcr.io/emu-dev/",
    )
    dist_parser.add_argument(
        "--dest", default=os.path.join(os.getcwd(), "src"), help="Destination for the generated docker files"
    )
    dist_parser.add_argument("--git", action="store_true", help="Create a git commit, and push to destination.")
    dist_parser.add_argument(
        "--sys", action="store_true", help="Write system image steps, otherwise write emulator steps."
    )
    dist_parser.add_argument(
        "emuzip",
        help="Zipfile containing the a publicly released emulator, or (canary|stable|[0-9]+) to use the latest canary, stable, or build id of the emulator to use. "
        "Keep in mind that using a build id can result in downloading an untested pre-release emulator build from the android ci server.",
    )
    dist_parser.add_argument(
        "img",
        default="P google_apis_playstore x86_64|Q google_apis_playstore x86_64",
        help="A regexp matching the image to retrieve. "
        "All the matching images will be selected when using a regex. "
        'Use the list command to show all available images. For example "P google_apis_playstore x86_64".',
    )
    dist_parser.set_defaults(func=create_cloud_build_distribuition)
    args = parser.parse_args()

    # Configure logger.
    lvl = logging.DEBUG if args.verbose else logging.WARNING
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter("%(log_color)s%(levelname)s:%(message)s"))
    logging.root = colorlog.getLogger("root")
    logging.root.addHandler(handler)
    logging.root.setLevel(lvl)

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
