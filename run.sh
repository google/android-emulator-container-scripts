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
CONTAINER_ID=$1
shift
PARAMS="$@"
docker run \
 --device /dev/kvm \
 --publish 8554:8554/tcp \
 --publish 5554:5554/tcp \
 --publish 5555:5555/tcp \
 -e TOKEN="$(cat ~/.emulator_console_auth_token)" \
 -e ADBKEY="$(cat ~/.android/adbkey)" \
 -e TURN \
 -e EMULATOR_PARAMS="${PARAMS}"  \
 ${CONTAINER_ID}
