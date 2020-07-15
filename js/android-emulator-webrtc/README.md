# android-emulator-webrtc

This contains a set of React components that can be used to interact with the android emulator from the browser. It is
intended to be used with an [envoy proxy](https://blog.envoyproxy.io/envoy-and-grpc-web-a-fresh-new-alternative-to-rest-6504ce7eb880)
that is connected to a running emulator.

See the [android container](https://github.com/google/android-emulator-container-scripts) scripts for an example on how to run
an emulator that is accessible via the web.

```
npm install --save android-emulator-webrtc
```

[Full reference](#full-reference)

## Features

- Display and interact with android emulator over the web, including audio if available.
- Retrieve logcat from remote emulator.
- Retrieve emulator status

---

## Usage

You can connect to remote unsecured emulator as follows:

```js
import { Emulator } from "android-emulator-webrtc/emulator";

class EmulatorScreen extends React.Component {
  render() {
    return <Emulator uri="https://my.emulator" />;
  }
}
```

In order to connect to a secure endpoint you will have to provide an authorization service that provides the following functions:

- `authHeader()` which must return a set of headers that should be send along with a request. For example:

```js
 authHeader = () => {
    return { Authorization: 'Some Token' };
  };
}
```

- `unauthorized()` a function that gets called when a 401 was received. Here you can provide logic to handle token refresh, re-login etc.

For example:

```js
import { Emulator } from "android-emulator-webrtc/emulator";

class EmulatorScreen extends React.Component {
  render() {
    return <Emulator uri="https://my.emulator" auth={my_auth_object} />;
  }
}
```

---

## Full Reference

## Emulator

A React component that displays a remote android emulator.

The emulator will mount a png or webrtc view component to display the current state
of the emulator. It will translate mouse events on this component and send them
to the actual emulator.

#### Authentication Service

The authentication service should implement the following methods:

- `authHeader()` which must return a set of headers that should be send along with a request.
- `unauthorized()` a function that gets called when a 401 was received.

#### Type of view

You usually want this to be webrtc as this will make use of the efficient
webrtc implementation. The png view will request screenshots, which are
very slow, and require the envoy proxy. You should not use this for remote emulators.

| prop                   |          type           |                      default                      |      required      | description                                                                                  |
| ---------------------- | :---------------------: | :-----------------------------------------------: | :----------------: | -------------------------------------------------------------------------------------------- |
| **auth**               |        `Object`         |                      `null`                       |        :x:         | The authentication service to use, or null for no authentication.                            |
| **height**             |        `Number`         |                                                   |        :x:         | The height of the component                                                                  |
| **muted**              |        `Boolean`        |                      `true`                       |        :x:         | True if the audio should be disabled. This is only relevant when using the webrtc engine.    |
| **onAudioStateChange** |       `Function`        | `(s) => { console.log("emulator audio: " + s); }` |        :x:         | Called when the audio becomes (un)available. True if audio is available, false otherwise.    |
| **onError**            |       `Function`        |          `(e) => { console.error(e); }`           |        :x:         | Callback that will be invoked in case of gRPC errors.                                        |
| **onStateChange**      |       `Function`        | `(s) => { console.log("emulator state: " + s); }` |        :x:         | Called upon state change, one of ["connecting", "connected", "disconnected"]                 |
| **poll**               |        `Boolean`        |                      `false`                      |        :x:         | True if polling should be used, only set this to true if you are using the go webgrpc proxy. |
| **uri**                |        `String`         |                                                   | :white_check_mark: | gRPC Endpoint where we can reach the emulator.                                               |
| **view**               | `Enum("webrtc", "png")` |                    `"webrtc"`                     |        :x:         | The underlying view used to display the emulator, one of ["webrtc", "png"]                   |
| **volume**             |        `Number`         |                       `1.0`                       |        :x:         | Volume between [0, 1] when audio is enabled. 0 is muted, 1.0 is 100%                         |
| **width**              |        `Number`         |                                                   |        :x:         | The width of the component                                                                   |

**Note**: The user must have interacted with the page before you can set the volume to "unmuted" (muted = false). Otherwise the video
will not play and will throw an error, which is currently not handled.

**Note**: The volume is the volume of the video element that is displayed, this is not the actual volume used inside the emulator. See this [support](https://support.google.com/android/answer/9082609?hl=en) document
on how to change the audio volume.

---

<a name="EmulatorStatus"></a>

## EmulatorStatus

**Kind**: global class

- [EmulatorStatus](#EmulatorStatus)
  - [new EmulatorStatus()](#new_EmulatorStatus_new)
  - [.getStatus](#EmulatorStatus.getStatus)
  - [.updateStatus](#EmulatorStatus.updateStatus)

<a name="new_EmulatorStatus_new"></a>

### new EmulatorStatus()

Gets the status of the emulator, parsing the hardware config into something
easy to digest.

| Param         | Type                                          | Description           |
| ------------- | --------------------------------------------- | --------------------- |
| uriOrEmulator | <code>string/EmulatorControllerService</code> | uri to gRPC endpoint. |
| auth          | <code>object</code>                           | authorization class.  |

<a name="EmulatorStatus.getStatus"></a>

### EmulatorStatus.getStatus

Gets the cached status.

**Kind**: static property of [<code>EmulatorStatus</code>](#EmulatorStatus)
<a name="EmulatorStatus.updateStatus"></a>

### EmulatorStatus.updateStatus

Retrieves the current status from the emulator.

**Kind**: static property of [<code>EmulatorStatus</code>](#EmulatorStatus)

| Param    | Type                  | Description                                                 |
| -------- | --------------------- | ----------------------------------------------------------- |
| fnNotify | <code>Callback</code> | when the status is available, returns the retrieved status. |
| cache    | <code>boolean</code>  | True if the cache can be used.                              |

<a name="Logcat"></a>

## Logcat
Observe the logcat stream from the emulator.

Streaming is done by either polling the emulator endpoint or making a streaming call.

It will send out the following events:

- `start` whenever the start method was called.
- `data` whenever new data became available.
- `end` whenever the stream is finished, either because it was stopped, or due to an error.

**Kind**: global class

* [Logcat](#Logcat)
    * [new Logcat(uriOrEmulator, auth)](#new_Logcat_new)
    * [.on](#Logcat.on)
    * [.off](#Logcat.off)
    * [.stop](#Logcat.stop)
    * [.start](#Logcat.start)

<a name="new_Logcat_new"></a>

### new Logcat(uriOrEmulator, auth)
Creates a logcat stream.

 The authentication service should implement the following methods:
- `authHeader()` which must return a set of headers that should be send along with a request.
- `unauthorized()` a function that gets called when a 401 was received.


| Param | Type |
| --- | --- |
| uriOrEmulator | <code>object</code> |
| auth | <code>object</code> |

<a name="Logcat.on"></a>

### Logcat.on
Register a listener.

**Kind**: static property of [<code>Logcat</code>](#Logcat)

| Param | Type | Description |
| --- | --- | --- |
| name | <code>string</code> | Name of the event. |
| fn | <code>Callback</code> | Function to notify on the given event. |

<a name="Logcat.off"></a>

### Logcat.off
Removes a listener.

**Kind**: static property of [<code>Logcat</code>](#Logcat)

| Param | Type | Description |
| --- | --- | --- |
| name | <code>string</code> | Name of the event. |
| fn | <code>Callback</code> | Function to notify on the given event. |

<a name="Logcat.stop"></a>

### Logcat.stop
Cancel the currently active logcat stream.

**Kind**: static property of [<code>Logcat</code>](#Logcat)
<a name="Logcat.start"></a>

### Logcat.start
Requests the logcat stream, invoking the callback when a log line arrives.

*Note:* Streaming can cause serious UI delays, so best not to use it.

**Kind**: static property of [<code>Logcat</code>](#Logcat)

| Param | Type | Description |
| --- | --- | --- |
| fnNotify | <code>Callback</code> | when a new log line arrives. |
| refreshRate | <code>number</code> | polling interval, or 0 if you wish to use streaming. |

