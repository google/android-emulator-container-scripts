#!/bin/sh
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

DOCKER_YAML=js/docker/docker-compose.yaml
PASSWDS="$USER,hello"

help() {
    cat <<EOF
       usage: create_web_container.sh [-h] [-a] [-s] -p user1,pass1,user2,pass2,...

       optional arguments:
       -h        show this help message and exit.
       -a        expose adb. Requires ~/.android/adbkey.pub to be available at container launch
       -s        start the container after creation.
       -p        list of username password pairs.  Defaults to: [${PASSWDS}]
EOF
    exit 1
}

panic() {
  echo $1
  exit 1
}

generate_pub_adb() {
  # Generate the adb public key, if it does not exist
  if [[ ! -f ~/.android/adbkey.pub ]]; then
    local ADB=adb
    if [ !   $(command -v $ADB >/dev/null 2>&1) ]; then
       ADB=$ANDROID_SDK_ROOT/platform-tools/adb
       command -v $ADB >/dev/null 2>&1 || panic "No public adb key, and adb not found in $ADB, make sure ANDROID_SDK_ROOT is set!"
    fi
    echo "Creating public key from private key with $ADB"
    $ADB pubkey  ~/.android/adbkey > ~/.android/adbkey.pub
  fi
}

while getopts 'hasp:' flag; do
    case "${flag}" in
    a) DOCKER_YAML=js/docker/docker-compose-with-adb.yaml ;;
    p) PASSWDS="${OPTARG}" ;;
    h) help ;;
    s) START='yes' ;;
    *) help ;;
    esac
done

# Make sure we have all we need for adb to succeed.
generate_pub_adb

. ./configure.sh >/dev/null

# Now generate the public/private keys and salt the password
cd js/jwt-provider
pip install -r requirements.txt >/dev/null
python gen-passwords.py --pairs "${PASSWDS}" || exit 1
cp jwt_secrets_pub.jwks ../docker/certs/jwt_secrets_pub.jwks
cd ../..


# Copy the private adbkey over
cp ~/.android/adbkey js/docker/certs

# compose the container
pip install docker-compose >/dev/null
docker-compose -f ${DOCKER_YAML} build
rm js/docker/certs/adbkey

if [ "${START}" = "yes" ]; then
    docker-compose -f ${DOCKER_YAML} up
else
    echo "Created container, you can launch it as follows:"
    echo "docker-compose -f ${DOCKER_YAML} up"
fi
