android-emulator-webrtc
=======================

This contains a set of React components that can be used to interact with the emulator from the browser. It is
intended to be used with an [envoy proxy](https://blog.envoyproxy.io/envoy-and-grpc-web-a-fresh-new-alternative-to-rest-6504ce7eb880)
that is connected to a running emulator.

```
npm install --save android-emulator-webrtc
```

[Full reference](#full-reference)

Features
--

- Display and interact with android emulator over the web.
- Retrieve logcat from remote emulator.
- Retrieve emulator status

---

## Usage

You can connect to remote unsecured emulator as follows:


```js
import { Emulator } from "android-emulator-webrtc/emulator";

class EmulatorScreen extends React.Component {

  render() {
    return (
        <Emulator uri='https://my.emulator' />
     );
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


---------------

Full Reference
---

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




Property | Type | Required | Default value | Description
:--- | :--- | :--- | :--- | :---
uri|string|yes||gRPC Endpoint where we can reach the emulator.
auth|object|no|null|The authentication service to use, or null for no authentication.
onStateChange|func|no||Called upon state change, one of [&quot;connecting&quot;, &quot;connected&quot;, &quot;disconnected&quot;]
width|number|no||The width of the component
height|number|no||The height of the component
view|enum|no|"webrtc"|The underlying view used to display the emulator, one of [&quot;webrtc&quot;, &quot;png&quot;]
poll|bool|no|false|True if polling should be used, only set this to true if you are using the go webgrpc proxy.
onError|func|no|&lt;See the source code&gt;|Callback that will be invoked in case of gRPC errors.
-----

<a name="EmulatorStatus"></a>

## EmulatorStatus
**Kind**: global class

* [EmulatorStatus](#EmulatorStatus)
    * [new EmulatorStatus()](#new_EmulatorStatus_new)
    * [.getStatus](#EmulatorStatus.getStatus)
    * [.updateStatus](#EmulatorStatus.updateStatus)

<a name="new_EmulatorStatus_new"></a>

### new EmulatorStatus()
Gets the status of the emulator, parsing the hardware config into something
easy to digest.

| Param | Type | Description |
| --- | --- | --- |
| uriOrEmulator | <code>string/EmulatorControllerService</code> | uri to gRPC endpoint. |
| auth | <code>object</code> | authorization class. |

<a name="EmulatorStatus.getStatus"></a>

### EmulatorStatus.getStatus
Gets the cached status.

**Kind**: static property of [<code>EmulatorStatus</code>](#EmulatorStatus)
<a name="EmulatorStatus.updateStatus"></a>

### EmulatorStatus.updateStatus
Retrieves the current status from the emulator.

**Kind**: static property of [<code>EmulatorStatus</code>](#EmulatorStatus)

| Param | Type | Description |
| --- | --- | --- |
| fnNotify | <code>Callback</code> | when the status is available, returns the retrieved status. |
| cache | <code>boolean</code> | True if the cache can be used. |




## Logcat
**Kind**: global class

* [Logcat](#Logcat)
    * [new Logcat()](#new_Logcat_new)
    * [.stop](#Logcat.stop)
    * [.start](#Logcat.start)

<a name="new_Logcat_new"></a>

### new Logcat()
Observe the logcat stream from the emulator.

This requires server side streaming and will only work with the envoy proxy.

| Param | Type | Description |
| --- | --- | --- |
| uriOrEmulator | <code>string/EmulatorControllerService</code> | uri to gRPC endpoint. |
| auth | <code>object</code> | authorization class. |

<a name="Logcat.stop"></a>

### Logcat.stop
 Cancel the currently active logcat stream.

**Kind**: static property of [<code>Logcat</code>](#Logcat)
<a name="Logcat.start"></a>

### Logcat.start
Requests the logcat stream.

**Kind**: static property of [<code>Logcat</code>](#Logcat)

| Param | Type | Description |
| --- | --- | --- |
| fnNotify | <code>Callback</code> | when a new log line arrives. |
