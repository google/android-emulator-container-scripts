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
VERBOSE=3
ANDROID_AVD_HOME=/root/.android/avd

# Return the value of a given named variable.
# $1: variable name
#
# example:
#    FOO=BAR
#    BAR=ZOO
#    echo `var_value $FOO`
#    will print 'ZOO'
#
var_value () {
    eval printf %s \"\$$1\"
}


# Return success if variable $1 is set and non-empty, failure otherwise.
# $1: Variable name.
# Usage example:
#   if var_is_set FOO; then
#      .. Do something the handle FOO condition.
#   fi
var_is_set () {
    test -n "$(var_value $1)"
}

_var_quote_value () {
    printf %s "$1" | sed -e "s|'|\\'\"'\"\\'|g"
}


# Append a space-separated list of items to a given variable.
# $1: Variable name.
# $2+: Variable value.
# Example:
#   FOO=
#   var_append FOO foo    (FOO is now 'foo')
#   var_append FOO bar    (FOO is now 'foo bar')
#   var_append FOO zoo    (FOO is now 'foo bar zoo')
var_append () {
    local _var_append_varname
    _var_append_varname=$1
    shift
    if test "$(var_value $_var_append_varname)"; then
        eval $_var_append_varname=\$$_var_append_varname\'\ $(_var_quote_value "$*")\'
    else
        eval $_var_append_varname=\'$(_var_quote_value "$*")\'
    fi
}

is_mounted () {
    mount | grep "$1"
}

# Run a command, output depends on verbosity level
run () {
    if [ "$VERBOSE" -lt 0 ]; then
        VERBOSE=0
    fi
    if [ "$VERBOSE" -gt 1 ]; then
        echo "COMMAND: $@"
    fi
    case $VERBOSE in
        0|1)
             eval "$@" >/dev/null 2>&1
             ;;
        2)
            eval "$@" >/dev/null
            ;;
        *)
            eval "$@"
            ;;
    esac
}


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
  run rm -f /root/.android/adbkey /root/.android/adbkey.pub

  if [ -s "/run/secrets/adbkey" ]; then
    echo "emulator: Copying private key from secret partition"
    run cp /run/secrets/adbkey /root/.android
  elif [ ! -z "${ADBKEY}" ]; then
    echo "emulator: Using provided adb private key"
    echo "-----BEGIN PRIVATE KEY-----" >/root/.android/adbkey
    echo $ADBKEY | tr " " "\\n" | sed -n "4,29p" >>/root/.android/adbkey
    echo "-----END PRIVATE KEY-----" >>/root/.android/adbkey
  elif [ ! -z "${ADBKEY_PUB}" ]; then
    echo "emulator: Using provided adb public key"
    echo $ADBKEY_PUB >>/root/.android/adbkey.pub
  else
    echo "emulator: No adb key provided, creating internal one, you might not be able connect from adb."
    run /android/sdk/platform-tools/adb keygen /root/.android/adbkey
  fi
  run chmod 600 /root/.android/adbkey
}

# Installs the console tokens, if any. The environment variable |TOKEN| will be
# non empty if a token has been set.
install_console_tokens() {
  if [ -s "/run/secrets/token" ]; then
    echo "emulator: Copying console token from secret partition"
    run cp /run/secrets/token /root/.emulator_console_auth_token
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
  run rm -rf /tmp/*
  run rm -rf ${ANDROID_AVD_HOME}/Pixel2.avd/*.lock

  # Check for core-dumps, that might be left over
  if ls core* 1>/dev/null 2>&1; then
    echo "emulator: ** WARNING ** WARNING ** WARNING **"
    echo "emulator: Core dumps exist in this image. This means the emulator has crashed in the past."
  fi

  mkdir -p /root/.android
}

setup_pulse_audio() {
  # We need pulse audio for the webrtc video bridge, let's configure it.
  run mkdir -p /root/.config/pulse
  export PULSE_SERVER=unix:/tmp/pulse-socket
  run pulseaudio -D -vvvv --log-time=1 --log-target=newfile:/tmp/pulseverbose.log --log-time=1 --exit-idle-time=-1
  tail -f /tmp/pulseverbose.log -n +1 | sed -u 's/^/pulse: /g' &
  run pactl list || exit 1
}

forward_loggers() {
  run mkdir /tmp/android-unknown
  run mkfifo /tmp/android-unknown/kernel.log
  run mkfifo /tmp/android-unknown/logcat.log
  echo "emulator: It is safe to ignore the warnings from tail. The files will come into existence soon."
  tail --retry -f /tmp/android-unknown/goldfish_rtc_0 | sed -u 's/^/video: /g' &
  cat /tmp/android-unknown/kernel.log | sed -u 's/^/kernel: /g' &
  cat /tmp/android-unknown/logcat.log | sed -u 's/^/logcat: /g' &
}

initialize_data_part() {
  # Check if we have mounted a data partition (tmpfs, or persistent)
  # and if so, we will use that as our avd directory.
  if  is_mounted /data; then
    run cp -fr /android-home/ /data
    ln -sf /data/android-home ${ANDROID_AVD_HOME}
    echo "path=${ANDROID_AVD_HOME}/Pixel2.avd" > ${ANDROID_AVD_HOME}/Pixel2.ini
  else
    ln -sf /android-home ${ANDROID_AVD_HOME}
  fi
}

# Let us log the emulator,script and image version.
log_version_info
initialize_data_part
clean_up
install_console_tokens
install_adb_keys
install_grpc_certs
setup_pulse_audio
forward_loggers

# Override config settings that the user forcefully wants to override.
if [ ! -z "${AVD_CONFIG}" ]; then
  echo "Adding ${AVD_CONFIG} to config.ini"
  echo "${AVD_CONFIG}" >>"${ANDROID_AVD_HOME}/Pixel2.avd/config.ini"
fi

# Launch internal adb server, needed for our health check.
# Once we have the grpc status point we can use that instead.
/android/sdk/platform-tools/adb start-server

# All our ports are loopback devices, so setup a simple forwarder
socat -d tcp-listen:5555,reuseaddr,fork tcp:127.0.0.1:5557 &

# Basic launcher command, additional flags can be added.
LAUNCH_CMD=emulator/emulator
var_append LAUNCH_CMD -avd Pixel2
var_append LAUNCH_CMD -ports 5556,5557 -grpc 8554 -no-window
var_append LAUNCH_CMD -skip-adb-auth -no-snapshot-save -wipe-data -no-boot-anim
var_append LAUNCH_CMD -shell-serial file:/tmp/android-unknown/kernel.log
var_append LAUNCH_CMD -logcat "*:V"
var_append LAUNCH_CMD -logcat-output /tmp/android-unknown/logcat.log
var_append LAUNCH_CMD -logcat "*:V"
var_append LAUNCH_CMD -feature AllowSnapshotMigration
var_append LAUNCH_CMD -gpu swiftshader_indirect {{extra}}

if [ ! -z "${EMULATOR_PARAMS}" ]; then
  var_append LAUNCH_CMD $EMULATOR_PARAMS
fi

if [ ! -z "${TURN}" ]; then
  var_append LAUNCH_CMD -turncfg \'${TURN}\'
fi

# Add qemu specific parameters
var_append LAUNCH_CMD -qemu -append panic=1

# Kick off the emulator
run exec $LAUNCH_CMD
# All done!
