# Android Emulator Container Scripts

This is a set of minimal scripts to run the emulator in a container for various
systems such as Docker, for external consumption. The scripts are compatible with
both Python version 2 and 3.

# Requirements

These demos are intended to be run on a linux OS. Your system must meet the following requirements:

- A Python interpreter must be installed.
- ADB must be available on the path. ADB comes as part of the [Android SDK](http://www.androiddocs.com/sdk/installing/index.html). Note that installing the command line tools is sufficient.
- [Docker](https://docs.docker.com/v17.12/install/) must be installed.
- [Docker-compose](https://docs.docker.com/compose/install/) must be installed.
- KVM must be available. You can get access to KVM by running on "bare metal", or on a (virtual) machine that provides [nested virtualization](https://blog.turbonomic.com/blog/). If you are planning to run this in the cloud (gce/azure/aws/etc..) you first must make sure you have access to KVM. Details on how to get access to KVM on the various cloud providers can be found here:

    - AWS provides [bare metal](https://aws.amazon.com/about-aws/whats-new/2019/02/introducing-five-new-amazon-ec2-bare-metal-instances/) instances that provide access to KVM.
    - Azure: Follow these [instructions](https://docs.microsoft.com/en-us/azure/virtual-machines/windows/nested-virtualization) to enable nested virtualization.
    - GCE: Follow these [instructions](https://cloud.google.com/compute/docs/instances/enable-nested-virtualization-vm-instances) to enable nested virtualization.


# Install

You can install the python package as follows:

    python setup.py install --user

This should make the  executable `emu-docker` available. You can get detailed information about the usage by launching it as follows:

    emu-docker -h

## Quick start, interactively creating a docker image

You can interactively select which version of android and emulator you wish to use by running:

    emu-docker interactive

You will be asked to select a system image and an emulator version, after which a docker file will be created.
The system image and emulator will be downloaded to the current directory if needed. If you wish to interact with
the emulator in the browser you will need to use a canary build!

You can now create the docker image by running:

    docker build src

A Docker image ID will output; use this to launch the container:

    ./run.sh <docker-image-id>

## Obtaining URLs for emulator/system image zip files

Issuing:

    emu-docker list

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


Given an emulator zip file and a system image zip file, we can build a
directory that can be sent to `docker build` via the following invocation of
`emu_docker`:

     emu_docker create <emulator-zip> <system-image-zip>  [--dest docker-src-dir (getcwd()/src by default)]

This places all the right elements to run a docker image, but does not build,
run or publish yet. A Linux emulator zip file must be used.

## Building the Docker image: Setting up the source dir

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

# Make the emulator accessible on the web

This repository also contains an example that demonstrates how you can use
docker to make the emulator accessible through the web. This is done by
composing the following set of docker containers:

- [Envoy](https://www.envoyproxy.io/), an edge and service proxy: The proxy is responsible for the following:
    - Offer TLS (https) using a self signed certificate
    - Redirect traffic on port 80 (http) to port 443 (https)
    - Act as a [gRPC proxy](https://grpc.io/blog/state-of-grpc-web/) for the emulator.
    - Redirect other requests to the Nginx component which hosts a [React](https://reactjs.org/) application.
- [Nginx](https://www.nginx.com/), a webserver hosting a compiled React App
- The emulator with a gRPC endpoint and a WebRTC video bridge.

## Important Notice!

In order to run this sample and be able to interact with the emulator you must keep the following in mind:

- The demo has two methods to display the emulator.
    1. Create an image every second, which is displayed in the browser. This approach will always work, but gives poor performance.
    2. Use [WebRTC](https://webrtc.org/) to display the state of the emulator in
       real time. This will only work if you are able to create a peer to peer connection
       to the server hosting the emulator. This is usually not a problem when your server
       is publicly visible, or if you are running the emulator on your own intranet.

- **There is no Authorization/Authentication:.** Anyone who can reach the website will be able to
  interact with the emulator. Which means they can control the emulator and run arbitrary code
  inside your emulator.

## Requirements

- You will need [docker-compose](https://docs.docker.com/compose/install/).
- You must have port 80 and 443 available. The docker containers will create an
  internal network and expose the http and https ports.
- You will need to create an emulator docker image, as described in the documentation above.

## Running the emulator on the web

Once you have taken care of the steps above you can create the containers as follows:

    docker-compose -f js/docker/docker-compose.yaml build

After building the containers, you can launch the emulator as follows

    docker-compose -f js/docker/docker-compose.yaml up

Point your browser to [localhost](http://localhost). You will likely get
a warning due to the usage of the self signed certifcate. Once you accept the
cert you should see the emulator in action

### Troubleshooting

Here are a list of things that we have seen with potential workarounds:

- **I am not seeing any video in the demo* when selecting webrtc*

  1. Click the png button. This will not use webrtc but request individual
     screenshots from the emulator. If this works you learn the following:

     - The emulator is running.
     - The gRPC endpoint is properly working.

      If the button does not show the emulator then you are possibly running
      an older emulator without gRPC support. Make sure you use the latest canary
      build.

  2. I do see video when using the png button.

     - Click the `webrtc` button. Make sure no video is showing.
     - Check the JavaScript console log.

     If you only see: `handleJsepMessage: {"start":{}}` then the
     video bridge is not running as expected. You could consult the logs for
     more info:  `docker logs docker_emulator_1 | egrep "pulse:|video:"`

    If you see something along the lines of:

     ```javascript
     handleJsepMessage: {"start":{}}
     jsep_protocol_driver.js:124 handleJsepMessage: {"sdp":"i...
     label:emulator_video_stream\r\n","type":"offer"}
     jsep_protocol_driver.js:76 handlePeerConnectionTrack: connecting [object
     RTCTrackEvent]
     webrtc_view.js:42 Connecting video stream: [object HTMLVideoElement]:0
     jsep_protocol_driver.js:124 handleJsepMessage:
     {"candidate":"candidate:3808623835 1 udp 2122260223 172.20.0.4 38033 typ
     host generation 0 ufrag kyFW network-id 1","sdpMLineIndex":0,"sdpMid":"0"}
     jsep_protocol_driver.js:124 handleJsepMessage:
     {"candidate":"candidate:2325047 1 udp 1686052607 104.132.0.73 59912 typ
     srflx raddr 172.20.0.4 rport 38033 generation 0 ufrag kyFW network-id
     1","sdpMLineIndex":0,"sdpMid":"0"}
     webrtc_view.js:50 Automatic playback started!
     ```

     You could be in a situation where
     a [TURN](https://en.wikipedia.org/wiki/Traversal_Using_Relays_around_NAT)
     is needed. This is usually only the case when you are in a restricted
     network. You can launch the emulator `$ANDROID_SDK_ROOT/emulator/emulator
     -help-turncfg` under linux to learn how to configure turn.
     You can pass use `emu_docker create --help` to learn how to pass the
     `--turncfg` flag to the emulator.


- **Credential errors when using docker-compose from virtual within a virtual
  environment:**

  The easiest solution is not to use docker-compose from a virtual environment.


### Modifying the demo

Details on how to modify can React application can be found [here](js/README.md)

