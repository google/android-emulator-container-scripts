#!/bin/bash

# This is the remote image we are going to run.
# Docker will obtain it for us if needed.
DOCKER_IMAGE=us-docker.pkg.dev/android-emulator-268719/images/r-google-x64:30.0.23

# This is the forwarding port. Higher ports are preferred as to not interfere
# with adb's ability to scan for emulators.
PORT=15555

# This will launch the container in the background.
container_id=$(docker run -d \
  --device /dev/kvm \
  --publish 8554:8554/tcp \
  --publish $PORT:5555/tcp \
  -e TOKEN="$(cat ~/.emulator_console_auth_token)" \
  -e ADBKEY="$(cat ~/.android/adbkey)" \
  -e EMULATOR_PARAMS="${PARAMS}" \
  $DOCKER_IMAGE)

echo "The container is running with id: $container_id"

# Note you might see something like:
# failed to connect to localhost:15555
# this merely indicates that the container is not yet ready.

echo "Connecting to forwarded adb port."
adb connect localhost:$PORT

# we basically have to wait until `docker ps` shows us as healthy.
# this can take a bit as the emulator needs to boot up!
echo "Waiting until the device is ready"
adb wait-for-device

# The device is now booting, or close to be booted
# We just wait until the sys.boot_completed property is set to 1.
while [ "$(adb shell getprop sys.boot_completed | tr -d '\r')" != "1" ]; do
  echo "Still waiting for boot.."
  sleep 1
done

echo "The device is ready"
echo "Run the following command to stop the container:"
echo "docker stop ${container_id}"
