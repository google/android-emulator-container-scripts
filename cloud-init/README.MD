# Android Emulator in the cloud

[Cloud-init](https://cloudinit.readthedocs.io/en/latest/) is a cross-platform cloud instance initialization standard that is widely supported. In this directory you will find a cloud-init scripts that can be used to configure a cloud instance with a running emulator.

# Requirements

You must run a base instance which has KVM and docker available. Details on how to get access to KVM on the various cloud providers can be found here:

- AWS provides [bare metal](https://aws.amazon.com/about-aws/whats-new/2019/02/introducing-five-new-amazon-ec2-bare-metal-instances/) instances that provide access to KVM.
- Azure: Follow these [instructions](https://docs.microsoft.com/en-us/azure/virtual-machines/windows/nested-virtualization) to enable nested virtualization.
- GCE: Follow these [instructions](https://cloud.google.com/compute/docs/instances/enable-nested-virtualization-vm-instances) to enable nested virtualization.

_NOTE_ You cannot use GCE's container optimized OS, as it does not make /dev/kvm available.

Follow the steps to for your cloud provider to create an image with:

- nested virtualization
- docker
- and cloud-init
- tmpfs with at least 8gb at emulator launch.

# Overview

The cloud-init file will launch a systemd service that will pull a public docker image and launch it. The systemd service will pull in the configuration file `/run/metadata/aemu` which contains a set of properties that modify the behavior of the emulator.

Most notable are:

- **GRPC_PORT**: The port where the gRPC service will be running. Defaults to 8554
- **ADB_PORT**: The port where ADB will be available. Defaults to 5555
- **TURN**: Configuration used to start turn server.
- **ADBKEY**: The private adb key that will be embedded in the emulator.
- **EMULATOR_IMG**: The url to a public docker image that will be launched. Defaults to `us-docker.pkg.dev/android-emulator-268719/images/30-google-x64:30.3.4`

First make sure the [cloud-init](cloud-init) file contains all the proper definitions needed for launch.

If you are running in gce you have the option the specify the properties above as metadata on the instance:

- emulator_grpc_port maps to GRPC_PORT
- emulator_adb_port maps to ADB_PORT
- emulator_image maps to EMULATOR_IMG
- emulator_adbkey maps to ADBKEY
- emulator_turn maps to TURN

# Lauching the instance

For example if you created a gce image with nested virtualization you can launch an instance as follows:


```sh
 gcloud compute instances create aemu-example \
              --zone us-west1-b  \
              --min-cpu-platform "Intel Haswell" \
              --image cos-dev-nested  \
              --machine-type n1-highcpu-32 \
              --tags=http-server,https-server \
              --metadata-from-file user-data=cloud-init \
              --emulator_adbkey="$(cat ~/.android/adbkey)",emulator_adb_port=80,emulator_grpc_port=443
```

Next you can connect to the emulator from your local machine as follows:

```sh
IP=$(gcloud compute instances describe aemu-example --format='get(networkInterfaces[0].accessConfigs[0].natIP)`)
adb connect $IP:80
```

Your device should now be available for access over adb.
