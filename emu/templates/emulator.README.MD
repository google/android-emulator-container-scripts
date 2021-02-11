## Android Emulator {{emu_build_id}} running Android-{{ro_build_version_sdk}} with {{qemu_tag}}
The Android Emulator simulates Android devices on your computer so that you can test your application on a variety of devices and Android API levels without needing to have each physical device.

The emulator provides almost all of the capabilities of a real Android device. You can simulate incoming phone calls and text messages, specify the location of the device, simulate different network speeds, simulate rotation and other hardware sensors, access the Google Play Store, and much more.

Testing your app on the emulator is in some ways faster and easier than doing so on a physical device.

### Requirements and recommendations
The docker images have the following requirements:

- Linux only. Launching the emulator in Windows or MacOS is not supported.
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

### Usage

The following environment variables are accepted by the emulator:

 - `TOKEN` This is the console authorization token. The console is available on port 5554
 - `ADBKEY` This is the private adb key, needed if you wish to make use of adb. ADB is available on port 5555.

The following ports are available:

 - 5554: The emulator [console](https://developer.android.com/studio/run/emulator-console) port.
 - 5555: The [Android Debug Bridge (adb)](https://developer.android.com/studio/command-line/adb) port
 - 8555: The gRPC port. This can be used by android studio and javascript endpoints.

An example invocation making the console, adb and the gRPC endpoint available:
```sh
docker run -e "TOKEN=$(cat ~/.emulator_console_auth_token)" -e "ADBKEY=$(cat ~/.android/adbkey)" -e "EMULATOR_PARAMS=${PARAMS}" --device /dev/kvm --publish 8554:8554/tcp --publish 5554:5554/tcp --publish 5555:5555/tcp ${CONTAINER_ID}
```

You might need to run `adb connect localhost:5555` to enable ADB to discover the device

### License

By making use of this container you accept the [Android Sdk License](https://developer.android.com/studio/terms)

The android emulator is released under the [Apache-2 license](http://www.apache.org/licenses/LICENSE-2.0).

The notices for the emulator and system image can be found in the following directories:

-  /android/sdk/system-images/android/x86_64/NOTICE.txt
-  /android/sdk/system-images/android/x86/NOTICE.txt
-  /android/sdk/emulator/NOTICE.txt

You can extract the notices as follows:

    CONTAINER_ID=$(docker create {{container_id}})
    docker export $CONTAINER_ID | tar vxf -  --wildcards --no-anchored 'NOTICE.txt'


### Metrics

{{metrics}}