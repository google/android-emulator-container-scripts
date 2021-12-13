# Copyright 2021 - The Android Open Source Project
#
# Licensed under the Apache License, Version 2_0 (the "License");
# you may not use this file except in compliance with the License_
# You may obtain a copy of the License at
#
#     http://www_apache_org/licenses/LICENSE-2_0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied_
# See the License for the specific language governing permissions and
# limitations under the License_
FROM alpine:3.3 AS unzipper
RUN apk add --update unzip

# Barely changes
FROM unzipper as sys_unzipper
COPY {{system_image_zip}} /tmp/
RUN unzip -u -o /tmp/{{system_image_zip}} -d /sysimg/

FROM nvidia/opengl:1.2-glvnd-runtime-ubuntu20.04
ENV NVIDIA_DRIVER_CAPABILITIES ${NVIDIA_DRIVER_CAPABILITIES},display

# Now we configure the user account under which we will be running the emulator
RUN mkdir -p /android/sdk/platforms && \
    mkdir -p /android/sdk/platform-tools && \
    mkdir -p /android/sdk/system-images

# Make sure to place files that do not change often in the higher layers
# as this will improve caching_
COPY platform-tools/adb /android/sdk/platform-tools/adb

ENV ANDROID_SDK_ROOT /android/sdk
WORKDIR /android/sdk
COPY --from=sys_unzipper /sysimg/ /android/sdk/system-images/android/
RUN chmod +x /android/sdk/platform-tools/adb

LABEL maintainer="{{user}}" \
    ro.system.build.fingerprint="{{ro_system_build_fingerprint}}" \
    ro.product.cpu.abi="{{ro_product_cpu_abi}}" \
    ro.build.version.incremental="{{ro_build_version_incremental}}" \
    ro.build.version.sdk="{{ro_build_version_sdk}}" \
    ro.build.flavor="{{ro_build_flavor}}" \
    ro.product.cpu.abilist="{{ro_product_cpu_abilist}}" \
    ro.build.type="{{ro_build_type}}" \
    SystemImage.TagId="{{SystemImage_TagId}}" \
    qemu.tag="{{qemu_tag}}" \
    qemu.cpu="{{qemu_cpu}}" \
    qemu.short_tag="{{qemu_short_tag}}" \
    qemu.short_abi="{{qemu_short_abi}}"

# We adopt the following naimg convention <ro.build.version.sdk>-<qem>-<ro.product.cpu.abi>
# SystemImage.TagId in 'aosp', 'google', 'playstore'ß
