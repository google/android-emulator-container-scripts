JavaScript WebRTC samples
=========================

This document descibes how to run the gRPC/WebRTC example. Support for WebRTC is officially only available on linux releases.
This sample expects the emulator to be running in a server like environment:

- There is a Webserver hosting the HTML/JS
- There is a [gRPC web proxy](https://grpc.io/blog/state-of-grpc-web/)
- The udp ports required for WebRTC are open, or a turn service is configured.

These services should be accessible for the browsers that want to interact with the emulator. For example a publicly visible GCE/AWS server should work fine.

This sample is based on ReactJS and provides the following set of components:

- Emulator: This component displays the emulator and will send mouse & keyboard events to it.
- LogcatView: A view that displays the current output of logcat. This currently relies on the material-ui theme.

Both components require the following properties to be set:

- `emulator`: This property must contain an `EmulatorControllerService` object.

You will likely need to modify `App.js` and `index.html` to suit your needs.

- There is a Webserver hosting the HTML/JS, we are using [NodeJs](https://nodejs.org/en/) for development.
- We are using [ReactJS](https://reactjs.org/) as our component framework.
- We use [Envoy](https://www.envoyproxy.io/) as the [gRPC web proxy](https://grpc.io/blog/state-of-grpc-web/).
- You are running [containerized](../README.MD) version of the emulator.

For fast video over [WebRTC](www.webrtc.org):

- You are using linux.
- You have android sdk installed, and the environment variable `ANDROID_SDK_ROOT` is set properly. The easiest way to install the sdk is by installing [Android Studio](https://developer.android.com/studio/install).
- An emulator build newer than 5769853. You can either:
  - Check if your current installed version will work. Run:
   ```sh
    $ $ANDROID_SDK_ROOT/emulator/emulator -version | head -n 1
    ```
    and make sure that the reported build_id is higher than 5769853
  - Build one from source yourself.
  - Obtain one from the [build bots](http://go/ab/emu-master-dev). Make sure to get sdk-repo-linux-emulator-XXXX.zip where XXXX is the build number. You can unzip the contents to `$ANDROID_SDK_ROOT`. For example:
  ```sh
    $ unzip ~/Downloads/sdk-repo-linux-emulator-5775474.zip -d $ANDROID_SDK_ROOT
  ```
- A valid virtual device to run inside the emulator. Instructions on how to create a virtual device can be found [here](https://developer.android.com/studio/run/managing-avds). Any virtual device can be used.
- [Node.js](https://nodejs.org/en/) Stable version 10.16.1 LTS or later.
- A [protobuf](https://developers.google.com/protocol-buffers/) compiler, version 3.6 or higher is supported.
- [Docker](https://www.docker.com). We will use the container infrastructure for easy deployment. Follow the instructions [here](http://go/installdocker) if you are within Google.


# Configure the emulator

Make sure you are able to launch the emulator from the command line with a valid avd. Instructions on how to create a virtual device can be found [here](https://developer.android.com/studio/run/managing-avds).

For example if you created a avd with the name P, you should be able to launch it as follows:

```sh
  $ $ANDROID_SDK_ROOT/emulator/emulator @P
```

Make sure that the emulator is working properly, and that can use the desired avd.

WebRTC support will be activated if the emulator is launched with the `-grpc <port>` flag. The current demos expect the gRPC endpoint to be available at `localhost:8554`. This port only needs to be accessible by the gRPC proxy that is being used. There is no need for this port to be publicly visible.

```sh
  $ $ANDROID_SDK_ROOT/emulator/emulator @P -grpc 8554
```

### Do I need TURN?

The most important thing to is to figure out if you need a [Turn Server](https://en.wikipedia.org/wiki/Traversal_Using_Relays_around_NAT).
**You usually only need this if your server running the emulator is behind a firewall, and not publicly accessible.**
Most of the time there is no need for a turn server. If you do have needs for a turn server you can follow the steps in the
[README](turn/README.MD).

# Internal Organization

This sample is based on ReactJS and uses the android-emulator-webrtc module to display the emulator.

- EmulatorScreen: This component displays the emulator and will send mouse & keyboard events to it.
- LogcatView: A view that displays the current output of logcat. This currently relies on the material-ui theme.

Both components require the following properties to be set:

- `uri`: This property must contain a URI to the gRPC proxy.
- `auth`: This property must contain an AuthService that implements the following two methods:
      - `authHeader()` which must return a set of headers that should be send along with a request. For example:
      ```js
          return { Authorization: "token header" };
      ```
      - `unauthorized()` a function that gets called when a 401 was received, here you can implement logic
         to make sure the next set of headers contain what is needed.

Components that you will need to include:
- **TokenAuthService**: An authentication service that provides a JWT token to the emulator.

You will likely need to modify `App.js` and `index.html` to suit your needs.

## As a Developer

As a developer you will make use of an envoy docker container and use node.js to serve the react app.  First you must
make sure you create a containerized version of the emulator as follows:

```sh
emu-docker create stable "Q google_apis_playstore x86"
```

This will binplace all the files needed for development under the src directory.
Next you can get the development environment ready by:


```sh
  $ make deps
```

And start envoy + nodejs as follows:

```
  $ make develop
```

This should open up a browser, and detect any change made to the webpages and JavaScript sources. Hit ctrl-c to stop the dev environment. Note that shutdown takes a bit as a docker container needs to shut down.

## Limitations

gRPC is not well supported in the browser and has only support for unary calls and server side streaming (when using envoy). This restricts support for other services such as [Waterfall](https://github.com/google/devx-tools/tree/master/waterfall).
