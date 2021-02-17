# Android Emulator in the cloud

[Cloud-init](https://cloudinit.readthedocs.io/en/latest/) is a cross-platform cloud instance initialization standard that is widely supported. In this directory you will find a cloud-init scripts that can be used to configure a cloud instance with a running emulator.

# Requirements

You must run a base instance which has KVM and docker available. Details on how to get access to KVM on the various cloud providers can be found here:

- AWS provides [bare metal](https://aws.amazon.com/about-aws/whats-new/2019/02/introducing-five-new-amazon-ec2-bare-metal-instances/) instances that provide access to KVM.
- Azure: Follow these [instructions](https://docs.microsoft.com/en-us/azure/virtual-machines/windows/nested-virtualization) to enable nested virtualization.
- GCE: Follow these [instructions](https://cloud.google.com/compute/docs/instances/enable-nested-virtualization-vm-instances) to enable nested virtualization.

_NOTE_ You cannot use GCE's container optimized OS, as it does not make /dev/kvm available. You can follow the steps at the bottom to create you own
version of a container optimized os with KVM enabled.

Follow the steps to for your cloud provider to create an image with:

- nested virtualization
- docker
- cloud-init
- tmpfs with at least 8gb per emulator that is launched.

# Overview

The cloud-init file will launch a systemd service that will pull a public docker image and launch it. The systemd service will pull in the configuration file `/run/metadata/aemu` which contains a set of properties that modify the behavior of the emulator.

Most notable are:

- **GRPC_PORT**: The port where the first instance of the gRPC service will be running. Defaults to 8554. The second instance will be available at 8555, etc.
- **ADB_PORT**: The port where the first instance of the ADB will be available. Defaults to 5555. The second instance will be available at 5556, etc.
- **INSTANCE_COUNT**: The number of emulators to start, defaults to 1. By default the emulator uses 4 vcpus, and 12gb per instance (4 gb memory, 8 gb tmpfs).
- **TURN**: Configuration used to start turn server.
- **ADBKEY**: The private adb key that will be embedded in the emulator.
- **EMULATOR_IMG**: The url to a public docker image that will be launched. Defaults to `us-docker.pkg.dev/android-emulator-268719/images/30-google-x64:latest`
- **AVD_CONFIG**: Additional avd configuration that should be added to the configuration. These parameters will be added to the config.ini of the launched avd.
- **EMULATOR_PARAMS**: Additional emulator parameters that should be added. These parameters are added to the launch of the emulator executable.

First make sure the [cloud-init](cloud-init) file contains all the proper definitions needed for launch.

If you are running in gce you have the option the specify the properties above as metadata on the instance:

- emulator_grpc_port maps to GRPC_PORT
- emulator_adb_port maps to ADB_PORT
- emulator_image maps to $IMAGE
- emulator_adbkey maps to ADBKEY
- emulator_turn maps to TURN
- emulator_instance_count maps to $INSTANCE_COUNT

Emulators are launched using the aemu.service systemd service. This service will start a series of emulators that are  named aemu_1, aemu_2, ..., aemu_n
Keep in mind that it can take a while to pull and launch the emulator, esp. if you are running more than one emulator.

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
              --metadata=emulator_adbkey="$(cat ~/.android/adbkey)",emulator_adb_port=80,emulator_grpc_port=443
```

Next you can connect to the emulator from your local machine as follows:

```sh
IP=$(gcloud compute instances describe aemu-example --format='get(networkInterfaces[0].accessConfigs[0].natIP)`)
adb connect $IP:80
```

Your device should now be available for access over adb.

## Building a container optimized os (cos) with kvm enabled.

Google provides a container optimized os for running docker images. Unfortunately the base images do not expose the
kvm kernels and cannot be used directly for the android emulator. In order to run them on gce you will have to
build your own cos image, with KVM enabled.

- First obtain the [cos source](https://cloud.google.com/container-optimized-os/docs/how-to/building-from-open-source#obtaining_the_source_code)
- Next apply the following changes:

```
diff --git a/project-lakitu/sys-kernel/lakitu-kernel-5_4/files/base.config b/project-lakitu/sys-kernel/lakitu-kernel-5_4/files/base.config
index e13a9e170e..a31b2b73db 100644
--- a/project-lakitu/sys-kernel/lakitu-kernel-5_4/files/base.config
+++ b/project-lakitu/sys-kernel/lakitu-kernel-5_4/files/base.config
@@ -609,7 +609,13 @@ CONFIG_EFI_EARLYCON=y

 CONFIG_HAVE_KVM=y
 CONFIG_VIRTUALIZATION=y
-# CONFIG_KVM is not set
+# is not set
+CONFIG_KVM=m
+CONFIG_KVM_INTEL=m
+CONFIG_KVM_MMU_AUDIT=m
+CONFIG_KVM_AMD=m
+CONFIG_VHOST_NET=m
+CONFIG_VHOST_VSOCK=m
 # CONFIG_VHOST_NET is not set
 # CONFIG_VHOST_SCSI is not set
 # CONFIG_VHOST_VSOCK is not set
```

in ./src/overlays

- Next follow the steps to build to [os](https://cloud.google.com/container-optimized-os/docs/how-to/building-from-open-source#building_a_image)
- Follow the steps to import the build into a system image in [gce](https://cloud.google.com/container-optimized-os/docs/how-to/building-from-open-source#running_on)

Next we need to create an image with nested virtualizaton enabled. In the steps below we assume that you imported the image as `emu-dev-cos-base` is `us-west1-b`:

    gcloud compute disks create cos-dev-nested-disk --image emu-dev-cos-base  --zone us-west1-b
    gcloud compute images create cos-dev-nested --source-disk cos-dev-nested-disk --source-disk-zone us-west1-b --licenses "https://www.googleapis.com/compute/v1/projects/vm-options/global/licenses/enable-vmx"

Congratulations! You have created a `cos-dev-nested` image with virtualization enabled that can be used in the examples above.


