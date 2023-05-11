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

PYTHON=python3
VENV=.venv

if [ ! -f "./$VENV/bin/activate" ]; then
  # Prefer python3 if it is available.
  if command -v python3 &>/dev/null; then
     echo "Using python 3"
     $PYTHON -m venv $VENV
     [ -e ./$VENV/bin/pip ] && ./$VENV/bin/pip install --upgrade pip
     [ -e ./$VENV/bin/pip ] && ./$VENV/bin/pip install --upgrade setuptools
  else
    echo "Using python 2 ----<< Deprecated! See: https://python3statement.org/.."
    echo "You need to upgrade to python3"
    exit 33
  fi
fi
if [ -e ./$VENV/bin/activate ]; then
   . ./$VENV/bin/activate
   pip install -e .
   echo "Ready to run emu-docker!"
fi
