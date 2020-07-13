/*
 * Copyright 2019 The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License")
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
import { EventEmitter } from "events";
import { Empty } from "google-protobuf/google/protobuf/empty_pb";
/**
 * This drives the jsep protocol with the emulator, and can be used to
 * send key/mouse/touch events to the emulator. Events will be send
 * over the data channel if open, otherwise they will be send via the
 * grpc endpoint.
 *
 *  The jsep protocol is described here:
 * https://rtcweb-wg.github.io/jsep/.
 *
 *  This class can fire two events:
 *
 * - `connected` when the stream has become available.
 * - `disconnected` when the stream broke down, or when we failed to establish a connection
 *
 * You usually want to start the stream after instantiating this object. Do not forget to
 * disconnect once you are finished to terminate the message pump.
 *
 *
 * @example
 *  jsep = new JsepProtocolDriver(emulator, s => { video.srcObject = s; video.play() });
 *  jsep.startStream();
 *
 * @export
 * @class JsepProtocol
 */
export default class JsepProtocol {
  /**
   * Creates an instance of JsepProtocol.
   * @param {EmulatorService} emulator Service used to make the gRPC calls
   * @param {RtcService} rtc Service used to open up the rtc calls.
   * @param {boolean} poll True if we should use polling
   * @param {callback} onConnect optional callback that is invoked when a stream is available
   * @param {callback} onDisconnect optional callback that is invoked when the stream is closed.
   * @memberof JsepProtocol
   */
  constructor(emulator, rtc, poll, onConnect, onDisconnect) {
    this.emulator = emulator;
    this.rtc = rtc;
    this.events = new EventEmitter();
    this.poll = poll;
    this.guid = null;
    this.event_forwarders = {};
    if (typeof this.rtc.receiveJsepMessages !== "function") this.poll = true;
    if (onConnect) this.events.on("connected", onConnect);
    if (onDisconnect) this.events.on("disconnected", onDisconnect);
  }

  on = (name, fn) => {
    this.events.on(name, fn);
  };

  /**
   * Disconnects the stream. This will stop the message pump as well.
   *
   * @memberof JsepProtocol
   */
  disconnect = () => {
    this.connected = false;
    if (this.peerConnection) this.peerConnection.close();
    this.active = false;
    this.events.emit("disconnected", this);
  };

  /**
   * Initiates the JSEP protocol.
   *
   * @memberof JsepProtocol
   */
  startStream = () => {
    const self = this;
    this.connected = false;
    this.peerConnection = null;
    this.active = true;

    var request = new Empty();
    this.rtc.requestRtcStream(request, {}, (err, response) => {
      // Configure
      self.guid = response;
      self.connected = true;

      if (!this.poll) {
        // Streaming envoy based.
        self._streamJsepMessage();
      } else {
        // Poll pump messages, go/envoy based proxy.
        console.info("Polling jsep messages.");
        self._receiveJsepMessage();
      }
    });
  };

  cleanup = () => {
    this.disconnect();
    if (this.peerConnection) {
      this.peerConnection.removeEventListener(
        "track",
        this._handlePeerConnectionTrack
      );
      this.peerConnection.removeEventListener(
        "icecandidate",
        this._handlePeerIceCandidate
      );
      this.peerConnection = null;
    }
    this.event_forwarders = {};
  };

  _handlePeerConnectionTrack = (e) => {
    this.events.emit("connected", e.track);
  };

  _handlePeerConnectionStateChange = (e) => {
    switch (this.peerConnection.connectionState) {
      case "disconnected":
      // At least one of the ICE transports for the connection is in the "disconnected" state
      // and none of the other transports are in the state "failed", "connecting",
      // or "checking".
      case "failed":
      // One or more of the ICE transports on the connection is in the "failed" state.
      case "closed":
        //The RTCPeerConnection is closed.
        this.disconnect();
    }
  };

  _handleDataChannelStatusChange = (e) => {
    console.log("Data status change " + e);
  };

  send(label, msg) {
    let bytes = msg.serializeBinary();
    let forwarder = this.event_forwarders[label];
    console.log("Send " + label + " " + JSON.stringify(msg.toObject()));
    // Send via data channel/gRPC bridge.
    if (this.connected && forwarder && forwarder.readyState == "open") {
      this.event_forwarders[label].send(bytes);
    } else {
      // Fallback to using the gRPC protocol
      switch (label) {
        case "mouse":
          this.emulator.sendMouse(msg);
          break;
        case "keyboard":
          this.emulator.sendKey(msg);
          break;
        case "touch":
          this.emulator.sendTouch(msg);
          break;
      }
    }
  }

  _handlePeerIceCandidate = (e) => {
    if (e.candidate === null) return;
    this._sendJsep({ candidate: e.candidate });
  };

  _handleDataChannel = (e) => {
    let channel = e.channel;
    this.event_forwarders[channel.label] = channel;
  };

  _handleStart = (signal) => {
    this.peerConnection = new RTCPeerConnection(signal.start);
    this.peerConnection.addEventListener(
      "track",
      this._handlePeerConnectionTrack,
      false
    );
    this.peerConnection.addEventListener(
      "icecandidate",
      this._handlePeerIceCandidate,
      false
    );
    this.peerConnection.addEventListener(
      "connectionstatechange",
      this._handlePeerConnectionStateChange,
      false
    );
    this.peerConnection.ondatachannel = (e) => {
      this._handleDataChannel(e);
    };
  };

  _handleSDP = async (signal) => {
    this.peerConnection.setRemoteDescription(new RTCSessionDescription(signal));
    const answer = await this.peerConnection.createAnswer();
    if (answer) {
      this.peerConnection.setLocalDescription(answer);
      this._sendJsep({ sdp: answer });
    } else {
      this.disconnect();
    }
  };

  _handleCandidate = (signal) => {
    this.peerConnection.addIceCandidate(new RTCIceCandidate(signal));
  };

  _handleJsepMessage = (message) => {
    try {
      const signal = JSON.parse(message);
      if (signal.start) this._handleStart(signal);
      if (signal.sdp) this._handleSDP(signal);
      if (signal.bye) this._handleBye();
      if (signal.candidate) this._handleCandidate(signal);
    } catch (e) {
      console.error("Failed to handle message: [" + message + "], due to: " + e);
    }
  };

  _handleBye = () => {
    if (this.connected) {
      this.disconnect();
    }
  };

  _sendJsep = (jsonObject) => {
    /* eslint-disable */
    var request = new proto.android.emulation.control.JsepMsg();
    request.setId(this.guid);
    request.setMessage(JSON.stringify(jsonObject));
    this.rtc.sendJsepMessage(request);
  };

  _streamJsepMessage = () => {
    if (!this.connected) return;
    var self = this;

    const stream = this.rtc.receiveJsepMessages(this.guid, {});
    stream.on("data", (response) => {
      const msg = response.getMessage();
      self._handleJsepMessage(msg);
    });
    stream.on("error", (e) => {
      self.cleanup();
    });
    stream.on("end", (e) => {
      self.cleanup();
    });

    this.receive = stream;
  };

  // This function is a fallback for v1 (go based proxy), that does not support streaming.
  _receiveJsepMessage = () => {
    if (!this.connected) return;

    var self = this;

    // This is a blocking call, that will return as soon as a series
    // of messages have been made available, or if we reach a timeout
    this.rtc.receiveJsepMessage(this.guid, {}, (err, response) => {
      const msg = response.getMessage();
      // Handle only if we received a useful message.
      // it is possible to get nothing if the server decides
      // to kick us out.
      if (msg) {
        self._handleJsepMessage(response.getMessage());
      }

      // And pump messages. Note we must continue the message pump as we
      // can receive new ICE candidates at any point in time.
      if (self.active) {
        self._receiveJsepMessage();
      }
    });
  };
}
