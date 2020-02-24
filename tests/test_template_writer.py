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

# Lint as: python3
"""Unit tests for the downloads_meu package.

"""

# Copyright 202 The Android Open Source Project
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

# Lint as: python3
"""Unit tests for the template writer

"""

import unittest
import tempfile
import os
import shutil

from emu.template_writer import TemplateWriter


class TemplateTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp("unittest")
        self.writer = TemplateWriter(self.tmpdir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_writer_writes_file(self):
        self.writer.write_template("cloudbuild.README.MD", {})
        self.assertTrue(os.path.exists(os.path.join(self.tmpdir, "cloudbuild.README.MD")))

    def test_renames_file(self):
        self.writer.write_template("cloudbuild.README.MD", {}, "foo")
        self.assertTrue(os.path.exists(os.path.join(self.tmpdir, "foo")))


if __name__ == "__main__":
    unittest.main()
