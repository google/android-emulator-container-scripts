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
import sys
"""This script prefixes the /* eslint-disable */ to the given file.

   For example:

   python eslint_prefix.py foo.js

   Will prefix /* eslint-disable */ to the file foo.js.
"""

def main(argv):
    prefix = '/* eslint-disable */'
    fname = argv[1]
    text = ''
    with open(fname, 'r') as fn:
        text = fn.read()

    with open(fname, 'w') as fn:
        fn.write(prefix)
        fn.write('\n')
        fn.write(text)

if __name__ == '__main__':
    main(sys.argv)