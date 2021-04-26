# Android Emulator Container Scripts

This is a set of minimal scripts to run the emulator in a container for various
systems such as Docker, for external consumption. The scripts are compatible
with both Python version 2 and 3.

\*Note that this is still an experimental feature and we recommend installing
this tool in a [python virtual environment](https://docs.python.org/3/tutorial/venv.html).
Please file issues if you notice that anything is not working as expected.

# Requirements

These demos are intended to be run on a linux OS. Your system must meet the
following requirements:

- A Python interpreter must be installed.
- ADB must be available on the path. ADB comes as part of the [Android
  SDK](http://www.androiddocs.com/sdk/installing/index.html). Note that
  installing the command line tools is sufficient.
- [Docker](https://docs.docker.com/v17.12/install/) must be installed. Make
  sure you can run it as [non-root
  user](https://docs.docker.com/install/linux/linux-postinstall/)
- [Docker-compose](https://docs.docker.com/compose/install/) must be installed.
- KVM must be available. You can get access to KVM by running on "bare metal",
  or on a (virtual) machine that provides nested virtualization. If you are planning to run
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
nested virtualization. The containers have been tested under Debian and Ubuntu running kernel 5.2.17.

_NOTE: The images will not run in docker on mac or windows_

# Quick start with hosted containers.

We now host a set of containers in a public repository. You can find details about the containers
[here](REGISTRY.MD). You can now run these containers without building them. For example:

```sh
docker run \
  -e ADBKEY="$(cat ~/.android/adbkey)" \
  --device /dev/kvm \
  --publish 8554:8554/tcp \
  --publish 5555:5555/tcp  \
  us-docker.pkg.dev/android-emulator-268719/images/30-google-x64:30.1.2
```

This will pull down the container if it is not locally available and launch it. You can see that is
starting:

After this you can connect to the device by configuring adb:

```sh
  adb connect localhost:5555
```

The device should now show up after a while as:

```sh
$ adb devices

List of devices attached
localhost:5555 device
```

If you wish to use this in a script you could do the following:

```sh
docker run -d \
  -e ADBKEY="$(cat ~/.android/adbkey)" \
  --device /dev/kvm \
  --publish 8554:8554/tcp \
  --publish 5555:5555/tcp  \
  us-docker.pkg.dev/android-emulator-268719/images/30-google-x64:30.1.2
  adb connect localhost:5555
  adb wait-for-device

  # The device is now booting, or close to be booted

```

A more detailed script can be found in [run-in-script-example.sh](./run-in-script-example.sh).

# Install in a virtual environment

You can install the python package as follows:

    source ./configure.sh

This will activate a virtual environment and make the executable `emu-docker`
available. You can get detailed information about the usage by launching it as
follows:

    emu-docker -h

You will have to accept the license agreements before you can create docker containers.

## Quick start, interactively creating and running a docker image

You can interactively select which version of android and emulator you wish to
use by running:

    emu-docker interactive --start

You will be asked to select a system image and an emulator version, after which
a docker file will be created. The system image and emulator will be downloaded
to the current directory if needed. The script will provide you with a command
to see the logs as well as the command to stop the container.

If the local adb server detected the started container automatically,
you have nothing to do to query it through adb. If that's not the case,
you can now connect to the running device using adb:

    adb connect localhost:5555

To check if adb has seen the container, you can use the:

    adb devices

command and check if a device is detected.

Do not forget to stop the docker container once you are done!

Read the [section](#Make-the-emulator-accessible-on-the-web) on making the
emulator available on the web to run the emulator using webrtc

## Obtaining URLs for emulator/system image zip files

Issuing:

    emu-docker list

will query the currently published Android SDK and output URLs for the zip files
of:

- Available and currently Docker-compatible system images
- Currently published and advertised emulator binaries

For each system image, the API level, variant, ABI, and URL are displayed. For
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
and system image. After the two are obtained, we can build a Docker image.

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

    docker run -e ADBKEY="$(cat ~/.android/adbkey)" \
    --device /dev/kvm \
    --publish 8554:8554/tcp \
    --publish 5555:5555/tcp <docker-image-id>

- Sets up the ADB key, assuming one exists at ~/.android/adbkey
- Uses `--device /dev/kvm` to have CPU acceleration
- Starts the emulator in the docker image with its gRPC service, forwarding the
  host ports 8554/5555 to container ports 8554/5555 respectively.
- The gRPC service is used to communicate with the running emulator inside the
  container.

You also have the option to mount a /data partition which the emulator will use
if available. This enables you to use a tmpfs which can give increased
performance, especially in the nested virtualization scenario.

For example:

    docker run -e ADBKEY="$(cat ~/.android/adbkey)" \
    --device /dev/kvm \
    --mount type=tmpfs,destination=/data \
    --publish 8554:8554/tcp \
    --publish 5555:5555/tcp <docker-image-id>

### Running the Docker image with GPU acceleration

We currently only support hardware acceleration for NVIDIA. In order to make use
of hardware acceleration you might have to install the NVIDIA docker extensions
from [here](https://github.com/NVIDIA/nvidia-docker) if you are running
an older version of docker (<19.03). You must make sure you have
a minimal X installation if you are using a cloud instance. For example
[Xvfb](https://en.wikipedia.org/wiki/Xvfb) can be used. You must build the
containers by passing in the --gpu flag:

    emu-docker create stable Q --gpu

You can now launch the emulator with the `run-with-gpu.sh` script:

    ./run-with-gpu.sh <docker-image-id> <additional-emulator-params>

The script is similar as to the one described above with the addition that it will:

- Make all the available gpu's available (`--gpu all`)
- Opens up xhost access for the container
- Enable the domain socket under /tmp/.X11-unix to communicate with hosts X server

Hardware acceleration will significantly improve performance of applications that heavily
rely on graphics. Note that even though we need a X11 server for gpu acceleration there
will be no ui displayed.

## Pushing images to a repository

You can push the created images to a repository by providing the --push and --repo and
--tag parameters when creating an image. The --tag parameter is optional and is used
to indicate the version of the created image. This will default to the build-id of the
emulator, as system images are rarely updated.

We adopted the following naming scheme for images:

{api}-{sort}-{abi}

Where:

- api is the api level
- sort is one of: _aosp_, _google_, _playstore_
  - _aosp_: A basic android open source image
  - _google_: A system image that includes access to Google Play services.
  - _playstore_: A system image that includes the Google Play Store app and access to Google Play services,
    including a Google Play tab in the Extended controls dialog that provides a
    convenient button for updating Google Play services on the device.
- abi indicates the underlying CPU architecture, which is one of: _x86_, _x64_, _a32_, _a64_.
  Note that arm images are not hardware accelerated and might not be fast enough.

For example: _29-playstore-x86:30.1.2_ indicates a playstore enabled system
image with Q running on 32-bit x86.

An example invocation for publishing all Q images to google cloud repo could be:

```sh
    emu-docker -v create --push --repo us.gcr.io/emulator-project/ stable "Q"
```

Images that have been pushed to a repository can be launched directly from the repository.
For example:

```sh
    docker run --device /dev/kvm --publish 8554:8554/tcp --publish 5555:5555/tcp \
    us.gcr.io/emulator-project/29-playstore-x86:30.1.2
```

## Communicating with the emulator in the container

## adb

We forward the port 5555 for adb access to the emulator running inside the
container. Adb might not automatically detect the device, so run:

    adb connect localhost:5555

Your device should now show up as:

```sh
$ adb devices

List of devices attached:
localhost:5555 device
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
- Depending on your network you might need [turn](js/turn/README.MD)

## Running the emulator on the web

In order to create the web containers you must have the following tools available:

- NodeJS
- Npm

Next you must create a container with the emulator & system image version you wish to
use. For example:

    . ./configure.sh && emu-docker create canary "P.*x64"

### Running the create script

Once you have taken care of the steps above you can create the containers using
the `create_web_container.sh` script:

```sh
$ ./create_web_container.sh -h
   usage: create_web_container.sh [-h] [-a] [-s] [-i] -p user1,pass1,user2,pass2,...

   optional arguments:
   -h        show this help message and exit.
   -a        expose adb. Requires ~/.android/adbkey.pub to be available at run.
   -s        start the container after creation.
   -p        list of username password pairs.  Defaults to: [jansene,hello]
   -i        install systemd service, with definition in /opt/emulator
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
- Note that the systemd service has only been tested on debian/ubuntu.

You can now launch the container as follows:

```sh
docker-compose -f js/docker/docker-compose.yaml up
```

If you wish to make ADB available you can apply the overlay found in
js/docker/development.yaml as follows:

```sh
docker-compose -f js/docker/docker-compose.yaml -f js/docker/development.yaml up
```

Point your browser to [localhost](http://localhost). You will likely get
a warning due to the usage of the self signed certificate. Once you accept the
cert you should be able to login and start using the emulator.

Keep the following things in mind when you make the emulator accessible over adb:

- Port 5555 will be exposed in the container.
- The container must have access to the file: `~/.android/adbkey`. This is
  the _PRIVATE_ key used by adb. Without this you will not be able to access the device
  over adb.
- The adb client you use to connect to the container must have access to the
  private key (~/.android/adbkey). This is usually the case if you are on the same machine.
- You must run: `adb connect ip-address-of-container:5555` before you can
  interact with the device. For example:

```sh
$ adb connect localhost:5555
$ adb shell getprop
```
# Creating cloud instances

There is a sample cloud-init script that provides details on how you can configure an instance
that will automatically launch and configure an emulator on creation. Details on how to do this
can be found [here](cloud-init/README.MD).

### Troubleshooting

We have a separate [document](TROUBLESHOOTING.md) related to dealing with
issues.

### Modifying the demo

Details on the design and how to modify the React application can be found
[here](js/README.md)
