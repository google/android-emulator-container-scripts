JavaScript WebRTC samples
=========================

This document describes the gRPC/WebRTC example. You can find instructions in [README](../README.MD) if you wis to run the web version. This document outlines the how you can extend or develop the web version further.

The web version relies on the following technologies;

- There is a Webserver hosting the HTML/JS, we are using [NodeJs](https://nodejs.org/en/) for development.
- We are using [ReactJS](https://reactjs.org/) as our component framework.
- We use [Envoy](https://www.envoyproxy.io/) as the [gRPC web proxy](https://grpc.io/blog/state-of-grpc-web/).
- You are running [containerized](../README.MD) version of the emulator.

For fast video over [WebRTC](www.webrtc.org):

- The udp ports required for WebRTC are open, or a turn service is configured.

### Do I need TURN?

The most important thing to is to figure out if you need a [Turn Server](https://en.wikipedia.org/wiki/Traversal_Using_Relays_around_NAT). **You usually only need this if your server running the emulator is behind a firewall, and not publicly accessible.** Most of the time there is no need for a turn server.

If for example you are running the emulator in a private Google GCE project, you will need to make use of a turn server. You can take the following steps to enable turn:

1. Enable a turn service. There are many services you could use. A quick [Google search](https://www.google.com/search?q=webrtc+turn+server+cloud+providers) will provide a series of provides. If you are internal at google you could use the [GCE turn api](http://go/turnaas).
2. Launch the emulator with the `-turncfg` flag.

   This will inform the videobridge to execute the given command for every new incoming connection to obtain the JSON turn configuration that will be used.

    This command must do the following:

    - Produce a result on stdout.
    - Produce a result within 1000 ms.
    - Produce a valid [JSON RTCConfiguration object](https://developer.mozilla.org/en-US/docs/Web/API/RTCConfiguration).
    - That contain at least an "iceServers" array.
    - The exit value should be 0 on success

    For example:

    ```sh
    emulator -grpc 8554 -turncfg "curl -s -X POST https://networktraversal.googleapis.com/v1alpha/iceconfig?key=MySec"
    ```

You can create the docker container with the `--extra` flag to pass in the turn configuration. For example:

```sh
emu-docker create stable \
           "O google_apis_playstore x86" \
           --extra  \
           '-turncfg "curl -s -X POST https://networktraversal.googleapis.com/v1alpha/iceconfig?key=mykey"' \
           --metrics
```

Would use the given curl command to obtain the the json snippet.

*NOTE: If you do not obtain ice configuration through curl you might need to modify the docker template
to make sure you can obtain the proper turn configuration.8

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
