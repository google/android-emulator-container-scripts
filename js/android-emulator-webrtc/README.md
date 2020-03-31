Android Emulator WebRTC
=======================

This contains an node module that can be used to interact with the emulator from the browser. It is
intended to be used with an envoy proxy.

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

gRPC is not well supported in the browser and has only support for unary calls and server side streaming. This restricts support for other services
such as [Waterfall](https://github.com/google/devx-tools/tree/master/waterfall).
