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

import emu_templates
import errno
import os
import shutil
import sys

from distutils.spawn import find_executable

from jinja2 import Environment, BaseLoader

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

if len(sys.argv) < 4:
    print("Invalid usage. Usage: python emu_docker.py <public-emu-zip> <public-sysimg-zip> <docker-repo-name> [docker-src-dir (cwd by default]")
    sys.exit(1)

src_dir = os.path.join(os.getcwd(), "src")

print(sys.argv)

emu_zip, sysimg_zip, repo_name = sys.argv[1:5]

if len(sys.argv) > 4:
    src_dir = sys.argv[4]

print("Emulator zip: %s" % emu_zip)
print("Sysimg zip: %s" % sysimg_zip)
print("Repo name: %s" % repo_name)

print("Docker src dir: %s" % src_dir)

mkdir_p(src_dir)

print("Copying zips to docker src dir...")
shutil.copy2(emu_zip, src_dir)
shutil.copy2(sysimg_zip, src_dir)
print("Done copying")

platform_tools_dir = os.path.join(src_dir, "platform-tools")
avd_dir_out_path = os.path.join(src_dir, "avd")
avd_dir_avd_out_path = os.path.join(src_dir, "avd", "Pixel2.avd")

print("Platform tools dir: %s" % platform_tools_dir)
print("AVD dir: %s" % avd_dir_avd_out_path)

print("Creating dirs...")

mkdir_p(platform_tools_dir)
mkdir_p(avd_dir_out_path)
mkdir_p(avd_dir_avd_out_path)

adb_loc = find_executable("adb")

print("Using adb: %s" % adb_loc)

shutil.copy2(adb_loc, platform_tools_dir)

avd_root_ini_out_path = os.path.join(avd_dir_out_path, "Pixel2.ini")
avd_config_ini_out_path = os.path.join(avd_dir_avd_out_path, "config.ini")

print("Writing config.ini and AVD info")

fh = open(avd_root_ini_out_path, 'w')
fh.write(emu_templates.avd_root_ini_template)
fh.close()

fh = open(avd_config_ini_out_path, 'w')
fh.write(emu_templates.avd_config_ini_template)
fh.close()

print("Writing launch-emulator.sh")

launch_emulator_out_path = os.path.join(src_dir, "launch-emulator.sh")
fh = open(launch_emulator_out_path, 'w')
fh.write(emu_templates.launch_emulator_sh_template)
fh.close()

print("Writing default.pa")

default_pa_out_path = os.path.join(src_dir, "default.pa")
fh = open(default_pa_out_path, 'w')
fh.write(emu_templates.default_pa_template)
fh.close()

print("Writing Dockerfile")

dockerfile_out_path = os.path.join(src_dir, "Dockerfile")

dockerfile_out_template = Environment(loader=BaseLoader).from_string(emu_templates.dockerfile_template)

with open(dockerfile_out_path, 'w') as dfile:
    dfile.write(
        dockerfile_out_template.render(
            user='{}@google.com'.format(os.environ["USER"]),
            tag="IMAGE_TEST_TAG",
            api="TEST_API",
            abi="TEST_ABI",
            emu_zip=emu_zip,
            emu_build_id="TEST_BUILD_ID",
            sysimg_zip=sysimg_zip,
            date="TEST_DATE"))

print("Done setting up Dockerfile")
