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

# We need pulse audio for the webrtc video bridge, let's configure it.
export PULSE_SERVER=unix:/tmp/pulse-socket
pulseaudio -D -vvvv --log-time=1 --log-target=newfile:/tmp/pulseverbose.log --log-time=1
tail -f /tmp/pulseverbose.log -n +1 | sed 's/^/pulse: /g' &
{ pactl list | sed 's/^/pulse: /g' ; } || echo "pulse: Unable to connect to pulse audio, WebRTC will not work."

# All our ports are loopback devices, so setup a simple forwarder
socat -d tcp-listen:5555,reuseaddr,fork tcp:127.0.0.1:6555 &
socat -d tcp-listen:5556,reuseaddr,fork tcp:127.0.0.1:6556 &

# Log all the video bridge interactions, note that his file comes into existence later on.
echo 'video: It is safe to ignore the 2 warnings from tail. The file will come into existence soon.'
tail --retry -f /tmp/android-unknown/goldfish_rtc_0 | sed 's/^/video: /g' &

# Kick off the emulator
exec emulator/emulator @Pixel2 -verbose -show-kernel -ports 6554,6555 -grpc 6556 -no-window -skip-adb-auth -logcat "*:v" {{extra}} "$@"

# All done!
