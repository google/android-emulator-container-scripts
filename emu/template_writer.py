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
import logging
from pathlib import Path
from typing import Dict

from jinja2 import Environment, PackageLoader


class TemplateWriter:
    """A Template writer uses Jinja to fill in templates.

    All the templates should live in the ./emu/templates directory.
    """

    def __init__(self, out_dir: str) -> None:
        """Creates a template writer that writes templates to the out_dir.

        The out directory will be created if needed.

        Args:
            out_dir (str): The directory where templates will be written.
        """
        self.env = Environment(loader=PackageLoader("emu", "templates"))
        self.dest = Path(out_dir)

    def _jinja_safe_dict(self, props: Dict[str, str]) -> Dict[str, str]:
        """Replaces all the . with _ in the keys of a dictionary.

        Args:
            props (dict): The dictionary to normalize.

        Returns:
            dict: A dictionary with keys normalized by replacing . with _.
        """
        return {key.replace(".", "_"): val for key, val in props.items()}

    def write_template(
        self, template_file: str, template_dict: Dict[str, str], rename_as: str = None
    ) -> Path:
        """Fill out the given template, writing it to the destination directory.

        Args:
            template_file (str): The name of the template file to fill.
            template_dict (dict): The dictionary to use to fill in the template.
            rename_as (str, optional): The name to use for the output file. Defaults to None.

        Returns:
            Path: The path to the written file.
        """
        dest_name = rename_as if rename_as else template_file
        return self._write_template_to(
            template_file, self.dest / dest_name, template_dict
        )

    def _write_template_to(
        self, tmpl_file: str, dest_file: Path, template_dict: Dict[str, str]
    ) -> None:
        """Loads the given template, writing it to the dest_file.

        Note: the template will be written {dest_dir}/{tmpl_file},
        directories will be created if the do not yet exist.

        Args:
            tmpl_file (str): The name of the template file.
            dest_file (pathlib.Path): The path to the file to be written.
            template_dict (dict): The dictionary to use to fill in the template.
        """
        template = self.env.get_template(tmpl_file)
        safe_dict = self._jinja_safe_dict(template_dict)
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        logging.info("Writing: %s -> %s with %s", tmpl_file, dest_file, safe_dict)
        with open(dest_file, "wb") as dfile:
            dfile.write(template.render(safe_dict).encode("utf-8"))
