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

import yaml

import emu.emu_downloads_menu as emu_downloads_menu
from emu.template_writer import TemplateWriter
from emu.process import run
from emu.generators.emulator_docker import EmulatorDockerFile
from emu.generators.system_image_docker import SystemImageDockerFile
from emu.utils import mkdir_p

def git_commit_and_push(dest):
    run(["git", "add", "--verbose", "*"], dest)
    run(["git", "commit", "-F", "README.MD"], dest)
    run(["git", "push"], dest)


def cloud_build(args):
    licenses = set(
        [x.license for x in emu_downloads_menu.get_emus_info()]
        + [x.license for x in emu_downloads_menu.get_images_info()]
    )

    for l in licenses:
        l.force_accept()

    mkdir_p(args.dest)
    imgzip = [args.img]
    if not os.path.exists(imgzip[0]):
        imgzip = [x.download() for x in emu_downloads_menu.find_image(imgzip[0])]

    emuzip = [args.emuzip]
    if emuzip[0] in ["stable", "canary", "all"]:
        emuzip = [x.download() for x in emu_downloads_menu.find_emulator(emuzip[0])]
    elif re.match("\d+", emuzip[0]):
        # We must be looking for a build id
        logging.info("Treating %s as a build id", emuzip[0])
        emuzip = [emu_downloads_menu.download_build(emuzip[0])]

    steps = []
    images = []
    emulators = set()
    build_step_id = 0

    for (img, emu) in itertools.product(imgzip, emuzip):
        logging.info("Processing %s, %s", img, emu)
        sys_docker = SystemImageDockerFile(img, args.repo)
        dest = os.path.join(args.dest, sys_docker.image_name())
        logging.info("Generating %s", dest)
        sys_docker.write(dest)

        build_step_id += 1
        step = sys_docker.create_cloud_build_step(dest)
        step["waitFor"] = ["-"]
        step["id"] = "step_{}".format(build_step_id)
        steps.append(step)
        images.append(sys_docker.full_name())
        images.append(sys_docker.latest_name())

        for metrics in [True, False]:
            device = EmulatorDockerFile(emu, sys_docker, args.repo, metrics)
            emulators.add(device.props["emu_build_id"])
            dest = os.path.join(args.dest, device.image_name())
            logging.info("Generating %s-> %s",device.image_name(), dest)
            device.write(dest)

            step = device.create_cloud_build_step(dest)
            step['waitFor'] = ["step_{}".format(build_step_id)]
            steps.append(step)
            images.append(device.full_name())
            images.append(device.latest_name())


    cloudbuild = {"steps": steps, "images": images, "timeout": "21600s"}
    with open(os.path.join(args.dest, "cloudbuild.yaml"), "w") as ymlfile:
        yaml.dump(cloudbuild, ymlfile)

    writer = TemplateWriter(args.dest)
    writer.write_template(
        "cloudbuild.README.MD",
        {"emu_version": ", ".join(emulators), "emu_images": "\n".join(["* {}".format(x) for x in images])},
        rename_as="README.MD",
    )
    writer.write_template(
        "registry.README.MD",
        {
            "emu_version": ", ".join(emulators),
            "emu_images": "\n".join(["* {}".format(x) for x in images]),
            "first_image": images[0]
        },
        rename_as="REGISTRY.MD",
    )

    if args.git:
        git_commit_and_push(args.dest)
