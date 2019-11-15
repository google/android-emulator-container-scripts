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

# This launcher will force the emulator to use hardware acceleration. In order to use this you will need to have
# installed the nvida docker container drivers (https://github.com/NVIDIA/nvidia-docker)
CONTAINER_ID=$1
shift
PARAMS="$@"
# Allow display access from the container.
xhost +si:localuser:root
docker run --gpus all -e DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix -e "ADBKEY=$(cat ~/.android/adbkey)" -e "EMULATOR_PARAMS=-gpu host ${PARAMS}" --device /dev/kvm --publish 5556:5556/tcp --publish 5555:5555/tcp ${CONTAINER_ID}
