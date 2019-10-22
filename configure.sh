#!/bin/sh
# Copyright 2019 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
if [ "${BASH_SOURCE-}" = "$0" ]; then
    echo "You must source this script: \$ source $0" >&2
    echo "It will create a virtual environment in which emu-docker will be installed."
    exit 33
fi

PYTHON=python

if [ ! -f "./venv/bin/activate" ]; then
  # Prefer python3 if it is available.
  if command -v python3 &>/dev/null; then
    echo "Using python 3"
    PYTHON=python3
    $PYTHON -m venv venv
  else
    echo "Using python 2"
    command virtualenv &>/dev/null || { echo "This script relies on virtualenv, you can install it with 'pip install virtualenv' (https://virtualenv.pypa.io)"; return ; }
    virtualenv venv
  fi
fi

. ./venv/bin/activate
$PYTHON setup.py develop

echo "Ready to run emu-docker!"