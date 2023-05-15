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
import pytest

from emu.template_writer import TemplateWriter


def test_writer_writes_file(temp_dir):
    writer = TemplateWriter(temp_dir)
    writer.write_template("cloudbuild.README.MD", {})
    assert (temp_dir / "cloudbuild.README.MD").exists()


def test_renames_file(temp_dir):
    writer = TemplateWriter(temp_dir)
    writer.write_template("cloudbuild.README.MD", {}, "foo")
    assert (temp_dir / "foo").exists()
