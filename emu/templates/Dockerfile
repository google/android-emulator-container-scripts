# Copyright 2019 - The Android Open Source Project
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
FROM alpine AS unzipper

RUN apk add --update unzip

COPY {{emu_zip}} /tmp/
RUN unzip -u -o /tmp/{{emu_zip}} -d /emu/


FROM nvidia/opengl:1.0-glvnd-runtime-ubuntu18.04 AS emulator
ENV NVIDIA_DRIVER_CAPABILITIES ${NVIDIA_DRIVER_CAPABILITIES},display

# Install all the required emulator dependencies.
# You can get these by running ./android/scripts/unix/run_tests.sh --verbose --verbose --debs | grep apt | sort -u
# pulse audio is needed due to some webrtc dependencies.
RUN apt-get update && apt-get install -y --no-install-recommends \
# Emulator & video bridge dependencies
    libc6 libdbus-1-3 libfontconfig1 libgcc1 \
    libpulse0 libtinfo5 libx11-6 libxcb1 libxdamage1 \
    libnss3 libxcomposite1 libxcursor1 libxi6 \
    libxext6 libxfixes3 zlib1g libgl1 pulseaudio socat \
# Enable turncfg through usage of curl
    curl ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Now we configure the user account under which we will be running the emulator
RUN mkdir -p /android/sdk/platforms && \
    mkdir -p /android/sdk/platform-tools && \
    mkdir -p /android/sdk/system-images && \
    mkdir -p /android-home

# Make sure to place files that do not change often in the higher layers
# as this will improve caching.
COPY launch-emulator.sh /android/sdk/
COPY platform-tools/adb /android/sdk/platform-tools/adb
COPY default.pa /etc/pulse/default.pa
RUN gpasswd -a root audio && \
    chmod +x /android/sdk/launch-emulator.sh /android/sdk/platform-tools/adb

COPY --from=unzipper /emu/ /android/sdk/

COPY avd /android-home
# Create an initial snapshot so we will boot fast next time around,
# This is currently an experimental feature, and is not easily configurable//
# RUN --security=insecure cd /android/sdk && ./launch-emulator.sh -quit-after-boot 120

# Open up adb & grpc port
EXPOSE 5555
EXPOSE 5556
ENV ANDROID_SDK_ROOT /android/sdk
ENV ANDROID_AVD_HOME /android-home
WORKDIR /android/sdk

# You will need to make use of the grpc snapshot/webrtc functionality to actually interact with
# the emulator.
CMD ["/android/sdk/launch-emulator.sh"]

# Note we should use gRPC status endpoint to check for health once the canary release is out.
HEALTHCHECK --interval=30s \
            --timeout=30s \
            --start-period=30s \
            --retries=3 \
            CMD /android/sdk/platform-tools/adb -s emulator-6554 shell getprop dev.bootcomplete | grep "1"

FROM unzipper as sys_unzipper

COPY {{sysimg_zip}} /tmp/
RUN unzip -u -o /tmp/{{sysimg_zip}} -d /sysimg/

FROM emulator

COPY --from=sys_unzipper /sysimg/ /android/sdk/system-images/android/
# Date frequently changes, so we place this in the last layer.
LABEL maintainer="{{user}}" \
      SystemImage.Abi={{abi}} \
      SystemImage.TagId={{tag}} \
      SystemImage.GpuSupport={{gpu}} \
      AndroidVersion.ApiLevel={{api}} \
      com.google.android.emulator.build-date="{{date}}" \
      com.google.android.emulator.description="Pixel 2 Emulator, running API {{api}}" \
      com.google.android.emulator.version="{{tag}}-{{api}}-{{abi}}/{{emu_build_id}}"
