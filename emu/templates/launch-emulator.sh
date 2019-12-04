#!/bin/sh
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

if [ -f "/run/secrets/adbkey.pub" ]; then
    echo "Copying key from secret partition"
    cp /run/secrets/adbkey.pub /root/.android
    chmod 600 /root/.android/adbkey.pub
elif [ ! -z "${ADBKEY}" ]; then
    echo "Using provided secret"
    echo "-----BEGIN PRIVATE KEY-----" > /root/.android/adbkey
    echo $ADBKEY | tr " " "\\n" | sed -n "4,29p" >> /root/.android/adbkey
    echo "-----END PRIVATE KEY-----" >> /root/.android/adbkey
    chmod 600 /root/.android/adbkey
else
    echo "No adb key provided.. You might not be able to connect to the emulator."
fi

# Override config settings that the user forcefully wants to override.
if [ ! -z "${AVD_CONFIG}" ]; then
  echo "Adding ${AVD_CONFIG} to config.ini"
  echo "${AVD_CONFIG}" >> "/android-home/Pixel2.avd/config.ini"
fi


# We need pulse audio for the webrtc video bridge, let's configure it.
mkdir -p /root/.config/pulse
export PULSE_SERVER=unix:/tmp/pulse-socket
pulseaudio -D -vvvv --log-time=1 --log-target=newfile:/tmp/pulseverbose.log --log-time=1 --exit-idle-time=-1
tail -f /tmp/pulseverbose.log -n +1 | sed 's/^/pulse: /g' &
pactl list || exit 1


# Launch internal adb server, needed for our health check.
# Once we have the grpc status point we can use that instead.
/android/sdk/platform-tools/adb start-server

# All our ports are loopback devices, so setup a simple forwarder
socat -d tcp-listen:5555,reuseaddr,fork tcp:127.0.0.1:6555 &

mkdir /tmp/android-unknown
mkfifo /tmp/android-unknown/kernel.log
mkfifo /tmp/android-unknown/logcat.log
echo "emulator: It is safe to ignore the warnings from tail. The files will come into existence soon."
tail --retry -f /tmp/android-unknown/goldfish_rtc_0 | sed 's/^/video: /g' &
cat /tmp/android-unknown/kernel.log | sed 's/^/kernel: /g' &
cat /tmp/android-unknown/logcat.log | sed 's/^/logcat: /g' &

# Kick off the emulator
exec emulator/emulator @Pixel2 -no-audio -verbose -ports 6554,6555 \
  -grpc 5556 -no-window -skip-adb-auth \
  -shell-serial file:/tmp/android-unknown/kernel.log \
  -logcat-output /tmp/android-unknown/logcat.log \
  -gpu swiftshader_indirect \
  {{extra}} ${EMULATOR_PARAMS} -qemu -append panic=1
# All done!
