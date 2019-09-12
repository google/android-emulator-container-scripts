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
import datetime
import logging
import os
import shutil
import socket
import sys
from distutils.spawn import find_executable
from errno import ENOENT

from jinja2 import Environment, PackageLoader

import emu
import emu.emu_downloads_menu as emu_downloads_menu
from emu.emu_downloads_menu import AndroidReleaseZip


def mkdir_p(path):
    """Make directories recursively if path not exists."""
    if not os.path.exists(path):
        os.makedirs(path)


def list_images(_):
    """Lists all the publicly available system and emlator images."""
    emu_downloads_menu.list_all_downloads()


def write_template(tmpl_file, dest_dir, template_dict):
    """Loads the the given template, writing it out to the dest_dir.

    Note: the template will be written {dest_dir}/{tmpl_file},
    directories will be created if the do not yet exist.
    """
    dest = os.path.join(dest_dir, tmpl_file)
    dest_dir = os.path.dirname(dest)
    mkdir_p(dest_dir)
    logging.info("Writing: %s", dest)
    env = Environment(loader=PackageLoader("emu", "templates"))
    template = env.get_template(tmpl_file)
    with open(dest, "w") as dfile:
        dfile.write(template.render(template_dict))


def create_docker(src_dir, emu_zip, sysimg_zip, repo_name="unused", extra=""):
    logging.info("Emulator zip: %s", emu_zip)
    logging.info("Sysimg zip: %s", sysimg_zip)
    logging.info("Repo name: %s", repo_name)
    logging.info("Docker src dir: %s", src_dir)

    adb_loc = find_executable("adb")
    if adb_loc is None:
        raise IOError(
            ENOENT, "Unable to find ADB on the path! Make sure that $ANDROID_SDK_ROOT/platform-tools is on the path")

    date = datetime.datetime.utcnow().isoformat("T") + "Z"
    sysimg_info = AndroidReleaseZip(sysimg_zip)

    # Make sure the destination directory is empty.
    shutil.rmtree(src_dir)
    mkdir_p(src_dir)

    print("Copying zips to docker src dir: {}".format(src_dir))
    shutil.copy2(emu_zip, src_dir)
    shutil.copy2(sysimg_zip, src_dir)
    logging.info("Done copying")

    platform_tools_dir = os.path.join(src_dir, "platform-tools")
    mkdir_p(platform_tools_dir)
    logging.info("Using adb: %s", adb_loc)
    shutil.copy2(adb_loc, platform_tools_dir)

    write_template("avd/Pixel2.ini", src_dir, {})
    write_template("avd/Pixel2.avd/config.ini", src_dir,
                   {"playstore": sysimg_info.tag() == "google_apis_playstore", "abi": sysimg_info.abi(), "tag": sysimg_info.tag()})
    write_template("launch-emulator.sh", src_dir,
                   {"extra": extra, "version": emu.__version__})
    write_template("default.pa", src_dir, {})
    write_template("Dockerfile", src_dir,
                   {
                       "user": "{}@{}".format(os.environ["USER"], socket.gethostname()),
                       "tag": sysimg_info.tag(),
                       "api": sysimg_info.api(),
                       "abi": sysimg_info.abi(),
                       "emu_zip": os.path.basename(emu_zip),
                       "emu_build_id": "TEST_BUILD_ID",
                       "sysimg_zip": os.path.basename(sysimg_zip),
                       "date": date})

    print("Created a Dockerfile in {}".format(src_dir))
    print("to create the image run:\n")
    print("docker build {}".format(src_dir))


def create_docker_image(args):
    """Create a directory containing all the necessary ingredients to construct a docker image."""
    create_docker(args.dest, args.emuzip, args.imgzip, args.repo, args.extra)


def create_docker_image_interactive(args):
    """Interactively create a docker image by selecting the desired combination from a menu."""
    img = emu_downloads_menu.select_image() or sys.exit(1)
    emulator = emu_downloads_menu.select_emulator() or sys.exit(1)

    img_zip = img.download()
    emu_zip = emulator.download("linux")
    create_docker(args.dest, emu_zip, img_zip, args.repo, args.extra)


def main():
    """Entry point that parses the argument, and invokes the proper functions."""

    parser = argparse.ArgumentParser(description="List and create emulator docker containers ({}).".format(emu.__version__),
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-v", "--verbose", dest="verbose", action="store_true",
                        help="Set verbose logging")

    subparsers = parser.add_subparsers()

    list_parser = subparsers.add_parser(
        "list", help="list all the available the publicly available emulators and system images.")
    list_parser.set_defaults(func=list_images)

    create_parser = subparsers.add_parser(
        "create", help="Given an emulator and system image zip file, generates a Docker image comprising complete environment in which the Android Emulator runs. After the Docker image is started up, interaction with the emulator is made possible via port forwarding and ADB, or gRPC and WebRTC.")
    create_parser.add_argument(
        "emuzip", help="Zipfile containing the a publicly released emulator.")
    create_parser.add_argument(
        "imgzip", help="Zipfile containing a public system image that should be launched.")
    create_parser.add_argument("--extra", default="",
                               help="Series of additional commands to pass on to the emulator. " +
                               'For example -turncfg \\"curl -s -X POST https://networktraversal.googleapis.com/v1alpha/iceconfig?key=MySec\\"')
    create_parser.add_argument("--dest", default=os.path.join(
        os.getcwd(), "src"), help="Destination for the generated docker files")
    create_parser.add_argument(
        "--repo", default="unused", help="Docker repository name")
    create_parser.set_defaults(func=create_docker_image)

    create_inter = subparsers.add_parser(
        "interactive", help="Interactively select which system image and emulator binary to use when creating a docker container")
    create_inter.add_argument("--extra", default="",
                              help="Series of additional commands to pass on to the emulator. " +
                              'For example -turncfg \\"curl -s -X POST https://networktraversal.googleapis.com/v1alpha/iceconfig?key=MySec\\"')
    create_inter.add_argument("--dest", default=os.path.join(
        os.getcwd(), "src"), help="Destination for the generated docker files")
    create_inter.add_argument(
        "--repo", default="unused", help="Docker repository name")
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
