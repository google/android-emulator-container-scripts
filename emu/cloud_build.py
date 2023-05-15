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
import itertools
import logging
import os
import re
import subprocess
from pathlib import Path

import yaml

import emu.emu_downloads_menu as emu_downloads_menu
from emu.containers.emulator_container import EmulatorContainer
from emu.containers.system_image_container import SystemImageContainer
from emu.emu_downloads_menu import accept_licenses
from emu.template_writer import TemplateWriter


def mkdir_p(path):
    """Make directories recursively if path not exists."""
    if not os.path.exists(path):
        os.makedirs(path)


def git_commit_and_push(dest):
    """Commit and pushes this cloud build to the git repo.

    Note that this can be *EXTREMELY* slow as you will likely
    have very large objects in your repo.

    Args:
        dest ({string}): The destination of the git repository.
    """
    subprocess.check_call(["git", "add", "--verbose", "*"], cwd=dest)
    subprocess.check_call(["git", "commit", "-F", "README.MD"], cwd=dest)
    subprocess.check_call(["git", "push"], cwd=dest)


def create_build_step(for_container, destination):
    build_destination = Path(destination) / for_container.image_name()
    logging.info("Generating %s", build_destination)
    for_container.write(build_destination)
    if for_container.can_pull():
        logging.warning("Container already available, no need to create step.")
        return {}

    step = for_container.create_cloud_build_step(for_container.image_name())
    step["waitFor"] = ["-"]
    step["id"] = for_container.image_name()
    logging.info("Adding step: %s", step)
    return step


def cloud_build(args):
    """Prepares the cloud build yaml and all its dependencies.

    The cloud builder will generate a single cloudbuild.yaml and generates the build
    scripts for every individual container.

    It will construct the proper dependencies as needed.
    """
    accept_licenses(True)

    mkdir_p(args.dest)
    image_zip = [args.img]

    # Check if we are building a custom image from a zip file
    if not os.path.exists(image_zip[0]):
        # We are using a standard image, we likely won't need to download it.
        image_zip = emu_downloads_menu.find_image(image_zip[0])

    emulator_zip = [args.emuzip]
    if emulator_zip[0] in ["stable", "canary", "all"]:
        emulator_zip = [x.download() for x in emu_downloads_menu.find_emulator(emulator_zip[0])]
    elif re.match(r"\d+", emulator_zip[0]):
        # We must be looking for a build id
        logging.warning("Treating %s as a build id", emulator_zip[0])
        emulator_zip = [emu_downloads_menu.download_build(emulator_zip[0])]

    steps = []
    images = []
    emulators = set()
    emulator_images = []

    for (img, emu) in itertools.product(image_zip, emulator_zip):
        logging.info("Processing %s, %s", img, emu)
        system_container = SystemImageContainer(img, args.repo)
        if args.sys:
            steps.append(create_build_step(system_container, args.dest))
        else:
            for metrics in [True, False]:
                emulator_container = EmulatorContainer(emu, system_container, args.repo, metrics)
                emulators.add(emulator_container.props["emu_build_id"])
                steps.append(create_build_step(emulator_container, args.dest))
                images.append(emulator_container.full_name())
                emulator_images.append(emulator_container.full_name())

    cloudbuild = {"steps": steps, "images": images, "timeout": "21600s"}
    logging.info("Writing cloud yaml [%s] in %s", yaml, args.dest)
    with open(os.path.join(args.dest, "cloudbuild.yaml"), "w", encoding="utf-8") as ymlfile:
        yaml.dump(cloudbuild, ymlfile)

    writer = TemplateWriter(args.dest)
    writer.write_template(
        "cloudbuild.README.MD",
        {"emu_version": ", ".join(emulators),
         "emu_images": "\n".join([f"* {x}" for x in emulator_images])},
        rename_as="README.MD",
    )
    writer.write_template(
        "registry.README.MD",
        {
            "emu_version": ", ".join(emulators),
            "emu_images": "\n".join([f"* {x}" for x in images]),
            "first_image": next(iter(images), None),
        },
        rename_as="REGISTRY.MD",
    )

    if args.git:
        git_commit_and_push(args.dest)
