# Known Issues

Here are a list of things that we have seen with potential workarounds:

## Why can't a use an image before O?

Releases before O are using an older linux kernel (3.10). This version of the
linux kernel has some issues that are under [active
investigation](https://issuetracker.google.com/issues/140881613).

## The container suddenly stopped and I cannot restart it.

It is possible that the emulator crashes or terminates unexpectedly. In this
case it is possible that the container gets into a corrupted state.

If this is the case you will have to delete the container:

```sh # stop the container docker stop CONTAINER_ID # removes the container
docker rm -f  CONTAINER_ID
```

## I am not seeing any video in the demo when selecting webrtc

1. Click the png button. This will not use webrtc but request individual
   screenshots from the emulator. If this works you learn the following:

    - The emulator is running.
    - The gRPC endpoint is properly working.

    If the button does not show the emulator then you are possibly running an
    older emulator without gRPC support. Make sure you use the latest canary
    build.

2. I do see video when using the png button.

    - Click the `webrtc` button. Make sure no video is showing.
    - Check the JavaScript console log.

    If you only see: `handleJsepMessage: {"start":{}}` then the video bridge is
    not running as expected. You could consult the logs for more info:  `docker
    logs docker_emulator_1 | egrep "pulse:|video:|version:"`

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
    a [TURN](https://en.wikipedia.org/wiki/Traversal_Using_Relays_around_NAT) is
    needed. This is usually only the case when you are in a restricted network.
    You can launch the emulator `$ANDROID_SDK_ROOT/emulator/emulator
    -help-turncfg` under linux to learn how to configure turn.  You can pass use
    `emu_docker create --help` to learn how to pass the `--turncfg` flag to the
    emulator.


## Credential errors with docker-compose

We have seen errors when running docker-compose from a virtual environment.

The easiest solution is not to use docker-compose from a virtual environment.
