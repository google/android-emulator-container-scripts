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

DOCKER_YAML=js/docker/docker-compose-build.yaml
PASSWDS="$USER,hello"

# Fancy colors in the terminal
if [ -t 1 ]; then
    RED=$(tput setaf 1)
    GREEN=$(tput setaf 2)
    RESET=$(tput sgr0)
else
    RED=
    GREEN=
    RESET=
fi

approve() {
    echo "${GREEN}I know what I'm doing..[y/n]?${RESET}"
    old_stty_cfg=$(stty -g)
    stty raw -echo
    answer=$(head -c 1)
    stty $old_stty_cfg # Careful playing with stty
    if echo "$answer" | grep -iq "^y"; then
        echo Yes
    else
        echo Ok, bye!
        exit 1
    fi
}

help() {
    cat <<EOF
       usage: create_web_container.sh [-h] [-a] [-s] [-i] -p user1,pass1,user2,pass2,...

       optional arguments:
       -h        show this help message and exit.
       -a        expose adb. Requires ~/.android/adbkey to be available at container launch
       -s        start the container after creation.
       -p        list of username password pairs.  Defaults to: [${PASSWDS}]
       -i        install systemd service, with definition in /opt/emulator
EOF
    exit 1
}

panic() {
    echo $1
    exit 1
}

generate_keys() {
    # Generate the adb public key, if it does not exist
    if [ ! -f ~/.android/adbkey ]; then
        local ADB=adb
        if [ ! command -v $ADB ] >/dev/null 2>&1; then
            ADB=$ANDROID_SDK_ROOT/platform-tools/adb
            command -v $ADB >/dev/null 2>&1 || panic "No adb key, and adb not found in $ADB, make sure ANDROID_SDK_ROOT is set!"
        fi
        echo "Creating public key from private key with $ADB"
        $ADB keygen ~/.android/adbkey
    fi
}

while getopts 'hasip:' flag; do
    case "${flag}" in
    a) DOCKER_YAML="${DOCKER_YAML} -f js/docker/development.yaml" ;;
    p) PASSWDS="${OPTARG}" ;;
    h) help ;;
    s) START='yes' ;;
    i) INSTALL='yes' ;;
    *) help ;;
    esac
done


# Create the javascript protobufs
make -C js deps

# Make sure we have all we need for adb to succeed.
generate_keys

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

if [ "${INSTALL}" = "yes" ]; then
    echo "Installing created container as systemd service"
    echo "This will copy the docker yaml files in /opt/emulator"
    echo "Make the current adbkey available to the image"
    echo "And activate the container as a systemd service."
    approve

    sudo mkdir -p /opt/emulator
    sudo cp ~/.android/adbkey /opt/emulator/adbkey
    sudo cp js/docker/docker-compose.yaml /opt/emulator/docker-compose.yaml
    sudo cp js/docker/production.yaml /opt/emulator/docker-compose.override.yaml
    sudo cp js/docker/emulator.service /etc/systemd/system/emulator.service
    sudo touch /etc/ssl/certs/emulator-grpc.cer
    sudo touch /etc/ssl/private/emulator-grpc.key
    sudo systemctl daemon-reload
    sudo systemctl enable emulator.service
    sudo systemctl restart emulator.service
fi
