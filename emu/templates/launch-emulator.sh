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

log_version_info() {
  # This function logs version info.
  emulator/emulator -version | head -n 1 | sed -u 's/^/version: /g'
  echo 'version: launch_script: {{version}}'
  img=$ANDROID_SDK_ROOT/system-images/android
  [ -f "$img/x86_64/source.properties" ] && cat "$img/x86_64/source.properties" | sed -u 's/^/version: /g'
  [ -f "$img/x86/source.properties" ] && cat "$img/x86/source.properties" | sed -u 's/^/version: /g'
}

install_adb_keys() {
  # We do not want to keep adb secrets around, if the emulator
  # ever created the secrets itself we will never be able to connect.
  rm -f /root/.android/adbkey /root/.android/adbkey.pub

  if [ -s "/run/secrets/adbkey" ]; then
    echo "emulator: Copying private key from secret partition"
    cp /run/secrets/adbkey /root/.android
  elif [ ! -z "${ADBKEY}" ]; then
    echo "emulator: Using provided adb private key"
    echo "-----BEGIN PRIVATE KEY-----" >/root/.android/adbkey
    echo $ADBKEY | tr " " "\\n" | sed -n "4,29p" >>/root/.android/adbkey
    echo "-----END PRIVATE KEY-----" >>/root/.android/adbkey
  else
    echo "emulator: No adb key provided, creating internal one, you might not be able connect from adb."
    adb keygen /root/.android/adbkey
  fi
  chmod 600 /root/.android/adbkey
}

# Installs the console tokens, if any. The environment variable |TOKEN| will be
# non empty if a token has been set.
install_console_tokens() {
  if [ -s "/run/secrets/token" ]; then
    echo "emulator: Copying console token from secret partition"
    cp /run/secrets/token /root/.emulator_console_auth_token
    TOKEN=yes
  elif [ ! -z "${TOKEN}" ]; then
    echo "emulator: Using provided emulator console token"
    echo ${TOKEN} >/root/.emulator_console_auth_token
  else
    echo "emulator: No console token provided, console disabled."
  fi

  if [ ! -z "${TOKEN}" ]; then
    echo "emulator: forwarding the emulator console."
    socat -d tcp-listen:5554,reuseaddr,fork tcp:127.0.0.1:5556 &
  fi
}

install_grpc_certs() {
    # Copy certs if they exists and are not empty.
    [ -s "/run/secrets/grpc_cer" ] && cp /run/secrets/grpc_cer /root/.android/emulator-grpc.cer
    [ -s "/run/secrets/grpc_key" ] && cp /run/secrets/grpc_key /root/.android/emulator-grpc.key
}

clean_up() {
  # Delete any leftovers from hard exits.
  rm -rf /tmp/*
  rm -rf /android-home/Pixel2.avd/*.lock

  # Check for core-dumps, that might be left over
  if ls core* 1>/dev/null 2>&1; then
    echo "emulator: ** WARNING ** WARNING ** WARNING **"
    echo "emulator: Core dumps exist in this image. This means the emulator has crashed in the past."
  fi

  mkdir -p /root/.android
}

setup_pulse_audio() {
  # We need pulse audio for the webrtc video bridge, let's configure it.
  mkdir -p /root/.config/pulse
  export PULSE_SERVER=unix:/tmp/pulse-socket
  pulseaudio -D -vvvv --log-time=1 --log-target=newfile:/tmp/pulseverbose.log --log-time=1 --exit-idle-time=-1
  tail -f /tmp/pulseverbose.log -n +1 | sed -u 's/^/pulse: /g' &
  pactl list || exit 1
}

forward_loggers() {
  mkdir /tmp/android-unknown
  mkfifo /tmp/android-unknown/kernel.log
  mkfifo /tmp/android-unknown/logcat.log
  echo "emulator: It is safe to ignore the warnings from tail. The files will come into existence soon."
  tail --retry -f /tmp/android-unknown/goldfish_rtc_0 | sed -u 's/^/video: /g' &
  cat /tmp/android-unknown/kernel.log | sed -u 's/^/kernel: /g' &
  cat /tmp/android-unknown/logcat.log | sed -u 's/^/logcat: /g' &
}

# Let's log the emulator,script and image version.
log_version_info
clean_up
install_console_tokens
install_adb_keys
install_grpc_certs
setup_pulse_audio
forward_loggers

# Override config settings that the user forcefully wants to override.
if [ ! -z "${AVD_CONFIG}" ]; then
  echo "Adding ${AVD_CONFIG} to config.ini"
  echo "${AVD_CONFIG}" >>"/android-home/Pixel2.avd/config.ini"
fi

# Launch internal adb server, needed for our health check.
# Once we have the grpc status point we can use that instead.
/android/sdk/platform-tools/adb start-server

# All our ports are loopback devices, so setup a simple forwarder
socat -d tcp-listen:5555,reuseaddr,fork tcp:127.0.0.1:5557 &

# Kick off the emulator
exec emulator/emulator @Pixel2 -no-audio -verbose -wipe-data \
  -ports 5556,5557 \
  -grpc 8554 -no-window -skip-adb-auth \
  -no-snapshot \
  -shell-serial file:/tmp/android-unknown/kernel.log \
  -logcat-output /tmp/android-unknown/logcat.log \
  -feature  AllowSnapshotMigration \
  -gpu swiftshader_indirect \
  {{extra}} ${EMULATOR_PARAMS} -qemu -append panic=1
# All done!
