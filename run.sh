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
docker run -e "ADBKEY=$(cat ~/.android/adbkey)" -e "EMULATOR_PARAMS=${PARAMS}" --device /dev/kvm --publish 5556:5556/tcp --publish 5555:5555/tcp ${CONTAINER_ID}
