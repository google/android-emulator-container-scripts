# Android Emulator Container Scripts

This is a set of minimal scripts to run the emulator in a container for various
systems such as Docker, for external consumption. The scripts are compatible with
both Python version 2 and 3.

# Install

The following Python libraries are required:

    urlfetch
    jinja2

They can be installed via `pip install urlfetch; pip install jinja2` (or use your favorite method).

# Docker

We have two scripts that work together to provide emulator docker images:

    emu_docker.py
    emu_download_menu.py

`emu_docker.py` sets up a Docker image source directory with a Dockerfile that is buildable and runnable as a Docker image, given a Linux emulator zip file, a system image zip file, and a docker repo name (currently unused; any name will do).

`emu_download_menu.py` lists a set of publically available Android Emulator system images and emulators along with their URLs, which makes it easier to download zip files for user with `emu_docker.py`.

## Obtaining URLs for emulator/system image zip files

Issuing:

    python emu_download_menu.py

will query the currently published Android SDK and output URLs for the zip files of:

- Available and currently Docker-compatible system images
- Currently published and advertised emulator binaries

For each system image, the API level, variant, ABI, and URL are displayed.  For
each emulator, the update channel (stable vs canary), version, host os, and URL
are displayed.

Example output:

    SYSIMG android 21 L x86_64 https://dl.google.com/android/repository/sys-img/android/x86_64-21_r05.zip
    SYSIMG android 22 L x86_64 https://dl.google.com/android/repository/sys-img/android/x86_64-22_r06.zip
    SYSIMG android 23 M x86_64 https://dl.google.com/android/repository/sys-img/android/x86_64-23_r10.zip
    SYSIMG android 24 N x86_64 https://dl.google.com/android/repository/sys-img/android/x86_64-24_r08.zip
    SYSIMG android 25 N x86_64 https://dl.google.com/android/repository/sys-img/android/x86_64-25_r01.zip
    SYSIMG android 26 O x86_64 https://dl.google.com/android/repository/sys-img/android/x86_64-26_r01.zip
    SYSIMG android 27 O x86_64 https://dl.google.com/android/repository/sys-img/android/x86_64-27_r01.zip
    SYSIMG android 28 P x86_64 https://dl.google.com/android/repository/sys-img/android/x86_64-28_r04.zip
    SYSIMG android 28 Q x86_64 https://dl.google.com/android/repository/sys-img/android/x86_64-Q_r04.zip
    SYSIMG google_apis 21 L x86_64 https://dl.google.com/android/repository/sys-img/google_apis/x86_64-21_r30.zip
    SYSIMG google_apis 22 L x86_64 https://dl.google.com/android/repository/sys-img/google_apis/x86_64-22_r24.zip
    SYSIMG google_apis 23 M x86_64 https://dl.google.com/android/repository/sys-img/google_apis/x86_64-23_r31.zip
    SYSIMG google_apis 24 N x86_64 https://dl.google.com/android/repository/sys-img/google_apis/x86_64-24_r25.zip
    SYSIMG google_apis 25 N x86_64 https://dl.google.com/android/repository/sys-img/google_apis/x86_64-25_r16.zip
    SYSIMG google_apis 26 O x86_64 https://dl.google.com/android/repository/sys-img/google_apis/x86_64-26_r13.zip
    SYSIMG google_apis 28 P x86_64 https://dl.google.com/android/repository/sys-img/google_apis/x86_64-28_r09.zip
    SYSIMG google_apis 28 Q x86_64 https://dl.google.com/android/repository/sys-img/google_apis/x86_64-Q_r04.zip
    SYSIMG google_apis_playstore 28 P x86_64 https://dl.google.com/android/repository/sys-img/google_apis_playstore/x86_64-28_r08.p
    SYSIMG google_apis_playstore 28 Q x86_64 https://dl.google.com/android/repository/sys-img/google_apis_playstore/x86_64-Q_r04.zp
    EMU stable 29.0.11 windows https://dl.google.com/android/repository/emulator-windows-5598178.zip
    EMU stable 29.0.11 macosx https://dl.google.com/android/repository/emulator-darwin-5598178.zip
    EMU stable 29.0.11 linux https://dl.google.com/android/repository/emulator-linux-5598178.zip
    EMU stable 28.0.25 windows https://dl.google.com/android/repository/emulator-windows-5395263.zip
    EMU canary 29.0.12 windows https://dl.google.com/android/repository/emulator-windows-5613046.zip
    EMU canary 29.0.12 macosx https://dl.google.com/android/repository/emulator-darwin-5613046.zip
    EMU canary 29.0.12 linux https://dl.google.com/android/repository/emulator-linux-5613046.zip

One can then use tools like `wget` or a browser to download a desired emulator
and system image.  After the two are obtained, we can build a Docker image.

## Building the Docker image: Setting up the source dir

Given an emulator zip file and a system image zip file, we can build a
directory that can be sent to `docker build` via the following invocation of
`emu_docker.py`:

    python emu_docker.py <emulator-zip> <system-image-zip> <docker-repo-name(unused currently)> [docker-src-dir (getcwd()/src by default)]

This places all the right elements to run a docker image, but does not build,
run or publish yet. A Linux emulator zip file must be used.

To build the Docker image corresponding to these emulators and system images:

    docker build <docker-src-dir, either ./src or specified argument to emu_docker.py>

A Docker image ID will output; save this image ID.

## Running the Docker image

We currently assume that KVM will be used with docker in order to provide CPU
virtualization capabilties to the resulting Docker image.

We provide the following run script:

    ./run.sh <docker-image-id>

It does the following:

    docker run -e "ADBKEY=$(cat ~/.android/adbkey)" --privileged  --publish 5556:5556/tcp --publish 5555:5555/tcp <docker-image-id>


- Sets up the ADB key, assuming one exists at ~/.android/adbkey
- Uses `--privileged` to have CPU acceleration
- Starts the emulator in the docker image with its gRPC service, forwarding the host ports 5556/5554 to container ports 5554/5554 respectively.
- The gRPC service is used to communicate with the running emulator inside the container.

## Communicating with the emulator in the container

## adb

We forward the port 5555 for adb access to the emulator running inside the
container (TODO: make this configurable per container).

To enable ADB access, run the following adb command, assuming no other emulators/devices connected:

    adb connect localhost:5555

## gRPC/webrtc

We use a gRPC/webrtc service to show what is on the emulator and to interact
with it.  This assumes that you have npm/node plus protoc 3.6+ installed and
available, and that no other node servers are running on your machine.

Checkout the emulator repo dir:

    https://android.googlesource.com/platform/external/qemu/+/refs/heads/emu-master-dev/android/android-grpc/docs/grpc-samples/js/


In the `/js` dir, issue:

    make deps # Uses npm and protoc 3.6+ libraries to build the client
    make develop # Runs the service

and point your web browser to localhost:3000.

To stop, hit Ctrl-C in the terminal where `make develop` was issued, then issue:

    make stop

TODO: We are also working on a more isolated solution via envoy, nginx, and `docker-compose`. See https://android.googlesource.com/platform/external/qemu/+/refs/heads/emu-master-dev/android/android-grpc/docs/grpc-samples/js/docker/

