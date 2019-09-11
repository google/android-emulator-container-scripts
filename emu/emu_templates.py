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

avd_root_ini_template = """
# Basic config used to create an avd for now.
avd.ini.encoding=UTF-8
path.rel=avd/Pixel2.avd
path=/android-home/Pixel2.avd
target=android
"""

avd_config_ini_template = """
AvdId=Pixel2
PlayStore.enabled=false
avd.ini.displayname=Pixel2
avd.ini.encoding=UTF-8
# Real Pixel2 ships with 32GB
disk.dataPartition.size=2G
fastboot.forceColdBoot=no
hw.accelerometer=yes
hw.audioInput=yes
hw.battery=yes
hw.camera.back=emulated
hw.camera.front=emulated
hw.cpu.ncore=4
hw.dPad=no
hw.device.hash2=MD5:bc5032b2a871da511332401af3ac6bb0
hw.device.manufacturer=Google
hw.gps=yes
hw.gpu.enabled=yes
hw.gpu.mode=auto
hw.initialOrientation=Portrait
hw.keyboard=yes
hw.mainKeys=no
hw.ramSize=4096
hw.sensors.orientation=yes
hw.sensors.proximity=yes
hw.trackBall=no
runtime.network.latency=none
runtime.network.speed=full
vm.heapSize=512
tag.display=Google APIs
# Set some
hw.lcd.density=440
hw.lcd.height=1920
hw.lcd.width=1080
# Unused
# hw.sdCard=yes
# sdcard.size=512M

# TODO: add support for other abis
tag.id=google_apis
abi.type=x86_64
hw.cpu.arch=x86_64
image.sysdir.1=system-images/android/x86_64/
"""

launch_emulator_sh_template = """#!/bin/sh
#
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


# Let's log the emulator,script and image  version.
emulator/emulator -version | head -n 1 | sed 's/^/version: /g'
echo 'version: launch_script: {{version}}'
img=$ANDROID_SDK_ROOT/system-images/android
[ -f "$img/x86_64/source.properties" ] && cat "$img/x86_64/source.properties"| sed 's/^/version: /g'
[ -f "$img/x86/source.properties" ] && cat "$img/x86/source.properties"| sed 's/^/version: /g'


# Delete any leftovers from hard exits.
rm -rf /tmp/*
rm -rf /android-home/Pixel2.avd/*.lock

# Check for core-dumps, that might be left over
if ls core* 1> /dev/null 2>&1; then
    echo "** WARNING ** WARNING ** WARNING **"
    echo "Core dumps exist in this image. This means the emulator has crashed in the past."
fi

# First we place the adb secret in the right place if it exists
mkdir -p /root/.android

if [ -f "/run/secrets/adbkey" ]; then
    echo "Copying key from secret partition"
    cp /run/secrets/adbkey /root/.android
    chmod 600 /root/.android/adbkey
elif [ ! -z "${ADBKEY}" ]; then
    echo "Using provided secret"
    echo "-----BEGIN PRIVATE KEY-----" > /root/.android/adbkey
    echo $ADBKEY | tr " " "\\n" | sed -n "4,29p" >> /root/.android/adbkey
    echo "-----END PRIVATE KEY-----" >> /root/.android/adbkey
    chmod 600 /root/.android/adbkey
else
    echo "No adb key provided.. You might not be able to connect to the emulator."
fi

# We need pulse audio for the webrtc video bridge, let's configure it.
export PULSE_SERVER=unix:/tmp/pulse-socket
pulseaudio -D -vvvv --log-time=1 --log-target=newfile:/tmp/pulseverbose.log --log-time=1
tail -f /tmp/pulseverbose.log -n +1 | sed 's/^/pulse: /g' &
{ pactl list | sed 's/^/pulse: /g' ; } || echo "pulse: Unable to connect to pulse audio, WebRTC will not work."

# All our ports are loopback devices, so setup a simple forwarder
socat -d tcp-listen:5555,reuseaddr,fork tcp:127.0.0.1:6555 &

# Log all the video bridge interactions, note that his file comes into existence later on.
echo 'video: It is safe to ignore the 2 warnings from tail. The file will come into existence soon.'
tail --retry -f /tmp/android-unknown/goldfish_rtc_0 | sed 's/^/video: /g' &

# Kick off the emulator
exec emulator/emulator @Pixel2 -verbose -show-kernel -ports 6554,6555 -grpc 5556 -no-window -gpu swiftshader_indirect -skip-adb-auth -logcat "*:v" {{extra}} "$@"

# All done!
"""

default_pa_template = """
# This is a NOP configuration for pulse audio, all audio goes nowhere!
load-module module-null-sink sink_name=NOP sink_properties=device.description=NOP
# Make pulse accessible on all channels. We only have null audio, and Docker
# should isolate our network anyways.
load-module module-native-protocol-unix auth-anonymous=1 socket=/tmp/pulse-socket
load-module module-native-protocol-tcp  auth-anonymous=1
"""

dockerfile_template = """
FROM debian:stretch-slim
LABEL maintainer="{{user}}" \\
      com.google.android.emulator.build-date="{{date}}" \\
      com.google.android.emulator.description="Pixel 2 Emulator, running API {{api}}" \\
      com.google.android.emulator.version="{{tag}}-{{api}}-{{abi}}/{{emu_build_id}}"

# Install all the required emulator dependencies.
# You can get these by running ./android/scripts/unix/run_tests.sh --verbose --verbose --debs | grep apt | sort -u
# pulse audio is needed due to some webrtc dependencies.
RUN apt-get update && apt-get install -y \\
# Needed for install / debug
    unzip \\
# Emulator & video bridge dependencies
    libc6 libdbus-1-3 libfontconfig1 libgcc1 \\
    libpulse0 libtinfo5 libx11-6 libxcb1 libxdamage1 \\
    libxext6 libxfixes3 zlib1g libgl1 pulseaudio socat

# Next we get an android image ready
# We explicitly curl the image from a public site to make sure we
# don't accidentally publish internal testing images.
# Now we configure the user account under which we will be running the emulator
RUN mkdir -p /android/sdk/platforms && \\
    mkdir -p /android/sdk/platform-tools && \\
    mkdir -p /android/sdk/system-images && \\
    mkdir -p /android-home

COPY {{emu_zip}} /android/sdk/
RUN unzip -u -o /android/sdk/{{emu_zip}} -d /android/sdk/ && \\
    rm /android/sdk/{{emu_zip}}

COPY {{sysimg_zip}} /android/sdk/
RUN unzip -u -o /android/sdk/{{sysimg_zip}} -d /android/sdk/system-images/android && \\
    rm /android/sdk/{{sysimg_zip}}

COPY launch-emulator.sh /android/sdk/
COPY default.pa /android/sdk/
COPY platform-tools /android/sdk/
COPY avd /android-home
COPY default.pa /etc/pulse/default.pa

RUN gpasswd -a root audio && \\
    chmod +x /android/sdk/launch-emulator.sh

# Create an initial snapshot so we will boot fast next time around,
# This is currently an experimental feature, and is not easily configurable.
# RUN --security=insecure cd /android/sdk && ./launch-emulator.sh -quit-after-boot 120

# Open up adb & grpc port
EXPOSE 5555
EXPOSE 5556
ENV ANDROID_SDK_ROOT /android/sdk
ENV ANDROID_AVD_HOME /android-home
WORKDIR /android/sdk

# Note, we will not be using gpu acceleration, nor will the emulator be visible.
# You will need to make use of the grpc snapshot/webrtc functionality to actually interact with
# the emulator.
CMD ["/android/sdk/launch-emulator.sh"]
"""

