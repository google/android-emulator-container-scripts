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

### Emulator
`Emulator` is an interactive view of the remote emulator. It is a
react component that you can insert into your application:

The following properties are defined:

```js
 static propTypes = {
    /** gRPC Endpoint where we can reach the emulator. */
    uri: PropTypes.string,
    /** The authentication service to use, or null for no authentication.
     *
     * The authentication service should implement the following methods:
     * - `authHeader()` which must return a set of headers that should be send along with a request.
     * - `unauthorized()` a function that gets called when a 401 was received.
     */
    auth: PropTypes.object,
    /** The width of the component */
    width: PropTypes.number,
    /** The height of the component */
    height: PropTypes.number,
    /** The underlying view used to display the emulator.
     *
     * You usually want this to be webrtc as this will make use of the efficient
     * webrtc implementation. The png view will request screenshots, which are
     * very slow. You should not use this for remote emulators.
     */
    view: PropTypes.oneOf(["webrtc", "png"]).isRequired,
    /** True if polling should be used, only set this to true if you are using the gowebrpc proxy. */
    poll: PropTypes.bool,
    /** Callback that will be invoked in case of gRPC errors. */
    onError: PropTypes.func
  };
```
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
