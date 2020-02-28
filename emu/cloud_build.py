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

import yaml
import click
import colorlog

import emu
import emu.emu_downloads_menu as emu_downloads_menu
from emu.docker_config import DockerConfig
from emu.docker_device import DockerDevice
from emu.template_writer import TemplateWriter


def cloud_build(args):
    licenses = set(
        [x.license for x in emu_downloads_menu.get_emus_info()]
        + [x.license for x in emu_downloads_menu.get_images_info()]
    )

    for l in licenses:
        l.force_accept()

    imgzip = [x.download() for x in emu_downloads_menu.find_image(args.img)]
    emuzip = [x.download() for x in emu_downloads_menu.find_emulator("canary")]
    devices = []

    steps = []
    images = []
    emulators = set()

    for (img, emu) in itertools.product(imgzip, emuzip):
        logging.info("Processing %s, %s", img, emu)
        img_rel = emu_downloads_menu.AndroidReleaseZip(img)
        if not img_rel.is_system_image():
            logging.warn("{} is not a zip file with a system image (Unexpected description), skipping".format(img))
            continue
        emu_rel = emu_downloads_menu.AndroidReleaseZip(emu)
        if not emu_rel.is_emulator():
            raise Exception("{} is not a zip file with an emulator".format(emu))

        emulators.add(emu_rel.build_id())
        for metrics in [True, False]:
            name = img_rel.repo_friendly_name()
            if not metrics:
                name += "-no-metrics"

            dest = os.path.join(args.dest, name)
            logging.info("Generating %s", name)
            device = DockerDevice(emu, img, dest, gpu=False, repo=args.repo, tag=emu_rel.build_id(), name=name)
            device.create_docker_file("", metrics=True, by_copying_zip_files=True)
            steps.append(device.create_cloud_build_step())
            images.append(device.tag)

    cloudbuild = {"steps": steps, "images": images}
    with open(os.path.join(args.dest, "cloudbuild.yaml"), "w") as ymlfile:
        yaml.dump(cloudbuild, ymlfile)

    writer = TemplateWriter(args.dest)
    writer.write_template(
        "cloudbuild.README.MD",
        {"emu_version": ", ".join(emulators), "emu_images": "\n".join(images)},
        rename_as="README.MD",
    )

