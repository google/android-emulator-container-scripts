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

# Minimal dependency script to create a Dockerfile for a particular combination of emulator and system image.

import argparse
import logging
import os
import sys

import emu
import emu.emu_downloads_menu as emu_downloads_menu
from emu.docker_device import DockerDevice


def list_images(args):
    """Lists all the publicly available system and emlator images."""
    emu_downloads_menu.list_all_downloads(args.arm)


def create_docker_image(args):
    """Create a directory containing all the necessary ingredients to construct a docker image."""
    imgzip = args.imgzip
    if not os.path.exists(imgzip):
        imgzip = emu_downloads_menu.find_image(imgzip).download()

    emuzip = args.emuzip
    if emuzip in ['stable', 'canary']:
        emuzip = emu_downloads_menu.find_emulator(emuzip).download()

    device = DockerDevice(emuzip, imgzip, args.dest, args.tag)
    device.create_docker_file(args.extra)
    img = device.create_container()
    if img and args.start:
        device.launch(img)


def create_docker_image_interactive(args):
    """Interactively create a docker image by selecting the desired combination from a menu."""
    img = emu_downloads_menu.select_image(args.arm) or sys.exit(1)
    emulator = emu_downloads_menu.select_emulator() or sys.exit(1)

    img_zip = img.download()
    emu_zip = emulator.download("linux")
    device = DockerDevice(emu_zip, img_zip, args.dest)
    device.create_docker_file(args.extra)
    img = device.create_container()
    if img and args.start:
        device.launch(img)


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

    create_parser = subparsers.add_parser(
        "create",
        help="Given an emulator and system image zip file, "
        "generates a Docker image comprising complete environment in which the Android Emulator runs. "
        "After the Docker image is started up, interaction with the emulator is made possible via port forwarding and ADB, "
        "or gRPC and WebRTC.",
    )
    create_parser.add_argument(
        "emuzip",
        help="Zipfile containing the a publicly released emulator, or [canary|stable] to use the latest canary or stable release.",
    )
    create_parser.add_argument(
        "imgzip",
        help='Zipfile containing a public system image that should be launched, or a regexp matching the image to retrieve. '
        'The first matching image will be selected when using a regex. '
        'Use the list command to show all available images. For example "P google_apis_playstore x86_64".',
    )
    create_parser.add_argument(
        "--extra",
        default="",
        help="Series of additional commands to pass on to the emulator. "
        + 'For example "-turncfg \\"curl -s -X POST https://networktraversal.googleapis.com/v1alpha/iceconfig?key=MySec\\""',
    )
    create_parser.add_argument(
        "--dest", default=os.path.join(os.getcwd(), "src"), help="Destination for the generated docker files"
    )
    create_parser.add_argument("--tag", default="", help="Docker image name")
    create_parser.add_argument(
        "--start",
        action="store_true",
        help="Starts the container after creating it. "
        "All exposed ports are forwarded, and your private adbkey (if available) is injected but not stored.",
    )
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
    create_inter.add_argument("--tag", default="", help="Docker image name")
    create_inter.set_defaults(func=create_docker_image_interactive)

    args = parser.parse_args()
    lvl = logging.DEBUG if args.verbose else logging.WARNING
    logging.basicConfig(level=lvl)
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
