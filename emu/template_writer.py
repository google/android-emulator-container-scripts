# Copyright 2020 The Android Open Source Project
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
import errno
import logging
import os

import docker
from jinja2 import Environment, PackageLoader
from packaging import version


from emu.utils import mkdir_p

import emu
from emu.android_release_zip import AndroidReleaseZip
from emu.platform_tools import PlatformTools


class TemplateWriter(object):
    """A Template writer uses jinja to fill in templates.

    All the templates should live in the ./emu/templates directory.
    """

    def __init__(self, out_dir):
        """Creates a template writer that writes templates to the out_dir

        The out directory will be created if needed.
        """
        self.env = Environment(loader=PackageLoader("emu", "templates"))
        self.dest = out_dir

    def _jinja_safe_dict(self, props):
        """Replace all the . with _ in the keys."""
        normalized = {}
        for k, v in props.items():
            normalized[k.replace(".", "_")] = v
        return normalized

    def write_template(self, template_file, template_dict, rename_as=None):
        """Fill out the given template, writing it to the destination directory."""
        dest_name = rename_as if rename_as else template_file
        return self._write_template_to(template_file, os.path.join(self.dest, dest_name), template_dict)

    def _write_template_to(self, tmpl_file, dest_file, template_dict):
        """Loads the the given template, writing it to the dest_file

        Note: the template will be written {dest_dir}/{tmpl_file},
        directories will be created if the do not yet exist.
        """
        template = self.env.get_template(tmpl_file)
        safe_dict = self._jinja_safe_dict(template_dict)
        mkdir_p(os.path.dirname(dest_file))
        logging.info("Writing: %s -> %s with %s", tmpl_file, dest_file, safe_dict)
        with open(dest_file, "wb") as dfile:
            dfile.write(template.render(safe_dict).encode("utf-8"))
