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
source ./configure.sh

# Now generate the public/private keys and salt the password
cd js/jwt-provider
pip install -r requirements.txt
python gen-passwords.py --pairs "$@" || exit 1
cp jwt_secrets_pub.jwks ../docker/certs/jwt_secrets_pub.jwks
cd ../..

# compose the container
pip install docker-compose
docker-compose -f js/docker/docker-compose.yaml build

echo "Created container, you can launch it as follows:"
echo "docker-compose -f js/docker/docker-compose.yaml up"