# Android Emulator Container Scripts

This is a set of minimal scripts to run the emulator in a container for various
systems such as Docker, for external consumption. The scripts are compatible
with both Python version 2 and 3.

*Note that this is still an experimental feature and we recommend installing
this tool in a [python virtual environment](https://docs.python.org/3/tutorial/venv.html).

# Requirements

These demos are intended to be run on a linux OS. Your system must meet the
following requirements:

- A Python interpreter must be installed.
- ADB must be available on the path. ADB comes as part of the [Android
  SDK](http://www.androiddocs.com/sdk/installing/index.html). Note that
  installing the command line tools is sufficient.
- [Docker](https://docs.docker.com/v17.12/install/) must be installed. Make
  sure you can run it as [non-root
  user]((https://docs.docker.com/install/linux/linux-postinstall/))
- [Docker-compose](https://docs.docker.com/compose/install/) must be installed.
- KVM must be available. You can get access to KVM by running on "bare metal",
  or on a (virtual) machine that provides [nested
  virtualization](https://blog.turbonomic.com/blog/). If you are planning to run
  this in the cloud (gce/azure/aws/etc..) you first must make sure you have
  access to KVM. Details on how to get access to KVM on the various cloud
  providers can be found here:

    - AWS provides [bare
      metal](https://aws.amazon.com/about-aws/whats-new/2019/02/introducing-five-new-amazon-ec2-bare-metal-instances/)
      instances that provide access to KVM.
    - Azure: Follow these
      [instructions](https://docs.microsoft.com/en-us/azure/virtual-machines/windows/nested-virtualization)
      to enable nested virtualization.
    - GCE: Follow these
      [instructions](https://cloud.google.com/compute/docs/instances/enable-nested-virtualization-vm-instances)
      to enable nested virtualization.

Keep in mind that you will see reduced performance if you are making use of
nested virtualization.


# Install in a virtual environment

You can install the python package as follows:

    source ./configure.sh

This will activate a virtual environment and make the executable `emu-docker`
available. You can get detailed information about the usage by launching it as
follows:

    emu-docker -h

## Quick start, interactively creating and running a docker image

You can interactively select which version of android and emulator you wish to
use by running:

    emu-docker interactive --start

You will be asked to select a system image and an emulator version, after which
a docker file will be created. The system image and emulator will be downloaded
to the current directory if needed. The script will provide you with a command
to see the logs as well as the command to stop the container.

You can now connect to the running device using adb:

    adb connect localhost:5555

Do not forget to stop the docker container once you are done!

If you wish to interact with the emulator via the web, and you have port 80 and
443 available you can run:

    docker-compose -f js/docker/docker-compose.yaml build

After building the containers, you can launch the emulator as follows

    docker-compose -f js/docker/docker-compose.yaml up

The emulator should be available at [http://localhost](http://localhost).

## Obtaining URLs for emulator/system image zip files

Issuing:

    emu-docker list

will query the currently published Android SDK and output URLs for the zip files
of:

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

Given an emulator zip file and a system image zip file, we can build a directory
that can be sent to `docker build` via the following invocation of `emu-docker`:

    emu-docker create <emulator-zip> <system-image-zip>  [--dest docker-src-dir
    (getcwd()/src by default)]

This places all the right elements to run a docker image, but does not build,
run or publish yet. A Linux emulator zip file must be used.

## Building the Docker image: Setting up the source dir

To build the Docker image corresponding to these emulators and system images:

    docker build <docker-src-dir, either ./src or specified argument to
    emu_docker.py>

A Docker image ID will output; save this image ID.

## Running the Docker image

We currently assume that KVM will be used with docker in order to provide CPU
virtualization capabilities to the resulting Docker image.

We provide the following run script:

    ./run.sh <docker-image-id> <additional-emulator-params>

It does the following:

    docker run -e "ADBKEY=$(cat ~/.android/adbkey)" --device /dev/kvm --publish
    5556:5556/tcp --publish 5555:5555/tcp <docker-image-id>


- Sets up the ADB key, assuming one exists at ~/.android/adbkey
- Uses `--device /dev/kvm` to have CPU acceleration
- Starts the emulator in the docker image with its gRPC service, forwarding the
  host ports 5556/6555 to container ports 5556/5555 respectively.
- The gRPC service is used to communicate with the running emulator inside the
  container.

### Running the Docker image with GPU acceleration

We currently only support hardware acceleration for NVIDIA. In order to make use
of hardware acceleration you might have to install the NVIDIA docker extensions
from [here](https://github.com/NVIDIA/nvidia-docker) if you are running
an older version of docker (<19.03). You must make sure you have
a minimal X installation if you are using a cloud instance. For example
[Xvfb](https://en.wikipedia.org/wiki/Xvfb) can be used.

You can now launch the emulator with the `run-with-gpu.sh` script:

    ./run-with-gpu.sh <docker-image-id> <additional-emulator-params>

The script is similar as to the one described above with the addition that it will:

  - Make all the available gpu's available (`--gpu all`)
  - Opens up xhost access for the container
  - Enable the domain socket under /tmp/.X11-unix to communicate with hosts X server

Hardware acceleration will significantly improve performance of applications that heavily
rely on graphics. Note that even though we need a X11 server for gpu acceleratation there
will be no ui displayed.

## Communicating with the emulator in the container

## adb

We forward the port 5555 for adb access to the emulator running inside the
container (TODO: make this configurable per container). Adb might not automatically
detect the device, so run:

    adb connect localhost:5555

Your device should now show up as:

```sh
$ adb devices

List of devices attached:
emulator-5554   device
```

# Make the emulator accessible on the web

This repository also contains an example that demonstrates how you can use
docker to make the emulator accessible through the web. This is done by
composing the following set of docker containers:

- [Envoy](https://www.envoyproxy.io/), an edge and service proxy: The proxy is
  responsible for the following:
    - Offer TLS (https) using a self signed certificate
    - Redirect traffic on port 80 (http) to port 443 (https)
    - Act as a [gRPC proxy](https://grpc.io/blog/state-of-grpc-web/) for the
      emulator.
    - Verifying tokens to permit access to the emulator gRPC endpoint.
    - Redirect other requests to the Nginx component which hosts
      a [React](https://reactjs.org/) application.
- [Nginx](https://www.nginx.com/), a webserver hosting a compiled React App
- [Token Service](js/jwt-provider/README.md) a simple token service that hands out
  [JWT](https://en.wikipedia.org/wiki/JSON_Web_Token) tokens to grant access to the emulator.
- The emulator with a gRPC endpoint and a WebRTC video bridge.

## Important Notice!

In order to run this sample and be able to interact with the emulator you must
keep the following in mind:

- The demo has two methods to display the emulator.
    1. Create an image every second, which is displayed in the browser. This
    approach will always work, but gives poor performance.
    2. Use [WebRTC](https://webrtc.org/) to display the state of the emulator in
       real time. This will only work if you are able to create a peer to peer
       connection to the server hosting the emulator. This is usually not
       a problem when your server is publicly visible, or if you are running the
       emulator on your own intranet.

## Requirements

- You will need [docker-compose](https://docs.docker.com/compose/install/).
- You must have port 80 and 443 available. The docker containers will create an
  internal network and expose the http and https ports.
- You will need to create an emulator docker image, as described in the
  documentation above.

## Running the emulator on the web

Once you have taken care of the steps above you can create the containers using
the `create_web_container.sh` script:

```sh
$ ./create_web_container.sh -h
   usage: create_web_container.sh [-h] [-a] [-s] -p user1,pass1,user2,pass2,...

   optional arguments:
   -h        show this help message and exit.
   -a        expose adb. Requires ~/.android/adbkey.pub to be available at run.
   -s        start the container after creation.
   -p        list of username password pairs.  Defaults to: [jansene,hello]
```

For example:

```sh
./create_web_container.sh -p user1,passwd1,user2,passwd2,....
```
This will do the following:

- Create a virtual environment
- Configure the token service to give access to the passed in users.
- Generate a public and private key pair, used to encrypt/decrypt JWT tokens
- Create the set of containers to interact with the emulator.

You can now launch the container as follows:

```sh
docker-compose -f js/docker/docker-compose.yaml up
```

Point your browser to [localhost](http://localhost). You will likely get
a warning due to the usage of the self signed certificate. Once you accept the
cert you should be able to login and start using the emulator.

Keep the following things in mind when you make the emulator accessible over adb:

- Port 5555 will be exposed in the container.
- The container must have access to the file: `~/.android/adbkey.pub`. This is
  the public key used by adb. If this file does not exist you can launch the
  emulator once to generate one for you.
- The adb client you use to connect to the container must have access to the
  private key (~/.android/adbkey).  This is usually the case if you are on the same machine.
- You must run: `adb connect ip-address-of-container:5555` before you can
  interact with the device. For example:

```sh
$ adb connect localhost:5555
$ adb shell getprop
```

### Troubleshooting

We have a separate [document](TROUBLESHOOTING.md) related to dealing with
issues.

### Modifying the demo

Details on the design and how to modify the React application can be found
[here](js/README.md)
