/**
 * @fileoverview Description of this file.
 */
/*
 * Copyright 2019 The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
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
import PropTypes from "prop-types";
import React, { Component } from "react";
import * as Device from "../../../android_emulation_control/emulator_controller_grpc_web_pb.js";

/**
 * This drives the JsepProtocol with the Emulator, it is basically an invisible React component.
 * Register the onConnect/onDisconnect callback properties to be informed of incoming/disconnected streams
 */
export default class JsepProtocol extends Component {

  constructor() {
    super()
    this.connected = false
    this.peerConnection = null
    /* eslint-disable */
    this.guid = new proto.android.emulation.control.RtcId()
  }

  static propTypes = {
    uri: PropTypes.string.isRequired, // gRPC endpoint of the emulator
    onConnect: PropTypes.func, // Callback when the video is ready to be show.
    onDisconnect: PropTypes.func, // Callback when the video is no longer availalb.e
  };

  static defaultProps = {
    onConnect: function () { },
    onDisconnect: function () { },
  };

  componentDidMount() {
    const { uri } = this.props;
    this.emulatorService = new Device.EmulatorControllerClient(uri);
    this.startStream();
  }

  componentWillUnmount() {
    this.cleanup()
  }

  disconnect = () => {
    const { onDisconnect } = this.props
    this.connected = false
    if (this.peerConnection) this.peerConnection.close()
    onDisconnect()
  }

  cleanup = () => {
    this.disconnect()
    if (this.peerConnection) {
      this.peerConnection.removeEventListener('track', this.handlePeerConnectionTrack)
      this.peerConnection.removeEventListener('icecandidate', this.handlePeerIceCandidate)
      this.peerConnection = null
    }
  }

  handlePeerConnectionTrack = e => {
    const { onConnect } = this.props
    console.log("handlePeerConnectionTrack: connecting " + e)
    onConnect(e.streams[0])
  }

  handlePeerConnectionStateChange = e => {
    const { onDisconnect } = this.props
    switch (this.peerConnection.connectionState) {
      case "disconnected":
      // At least one of the ICE transports for the connection is in the "disconnected" state
      // and none of the other transports are in the state "failed", "connecting",
      // or "checking".
      case "failed":
      // 	One or more of the ICE transports on the connection is in the "failed" state.
      case "closed":
        //The RTCPeerConnection is closed.
        onDisconnect()
    }
  }

  handlePeerIceCandidate = e => {
    if (e.candidate === null) return
    this.sendJsep({ candidate: e.candidate })
  }

  handleStart = signal => {
    this.peerConnection = new RTCPeerConnection(signal.start)
    this.peerConnection.addEventListener('track', this.handlePeerConnectionTrack, false)
    this.peerConnection.addEventListener('icecandidate', this.handlePeerIceCandidate, false)
    this.peerConnection.addEventListener('connectionstatechange', this.handlePeerConnectionStateChange, false)
  }

  handleSDP = async signal => {
    this.peerConnection.setRemoteDescription(new RTCSessionDescription(signal))
    const answer = await this.peerConnection.createAnswer()
    if (answer) {
      this.peerConnection.setLocalDescription(answer)
      this.sendJsep({ sdp: answer })
    } else {
      this.disconnect()
    }
  }

  handleCandidate = signal => {
    this.peerConnection.addIceCandidate(new RTCIceCandidate(signal))
  }

  handleJsepMessage = message => {
    try {
      console.log("handleJsepMessage: " + message)
      const signal = JSON.parse(message)
      if (signal.start) this.handleStart(signal)
      if (signal.sdp) this.handleSDP(signal)
      if (signal.bye) this.handleBye()
      if (signal.candidate) this.handleCandidate(signal)
    } catch (e) {
      console.log("Failed to handle message: [" + message + "], due to: " + e)
    }
  }

  handleBye = () => {
    if (this.connected) {
      this.disconnect()
    }
  }

  sendJsep = jsonObject => {
    /* eslint-disable */
    var request = new proto.android.emulation.control.JsepMsg()
    request.setId(this.guid)
    request.setMessage(JSON.stringify(jsonObject))
    this.emulatorService.sendJsepMessage(request, {},
      function (err, response) {
        if (err) {
          console.error(
            "Grpc: " + err.code + ", msg: " + err.message,
            "Emulator:updateview"
          );
        }
      });
  }

  startStream() {
    this.setState({ WebRTC: "connecting" })
    var self = this
    var request = new proto.google.protobuf.Empty()
    var call = this.emulatorService.requestRtcStream(request, {},
      function (err, response) {
        if (err) {
          console.error(
            "Grpc: " + err.code + ", msg: " + err.message,
            "Emulator:updateview"
          );
        } else {
          // Configure
          self.guid.setGuid(response.getGuid())
          self.connected = true

          // And pump messages
          self.receiveJsepMessage()
        }
      });
  }

  receiveJsepMessage() {
    if (!this.connected)
      return

    /* eslint-disable */
    var self = this;

    // This is a blocking call, that will return as soon as a series
    // of messages have been made available.
    this.emulatorService.receiveJsepMessage(this.guid, {},
      function (err, response) {
        if (err) {
          console.error(
            "Grpc: " + err.code + ", msg: " + err.message,
            "Emulator:updateview"
          );
        } else {
          const msg = response.getMessage()
          // Handle only if we received a useful message.
          // it is possible to get nothing if the server decides
          // to kick us out.
          if (msg)
            self.handleJsepMessage(response.getMessage())

          // And pump messages
          self.receiveJsepMessage()
        }
      });
  }


  render() {
    return null
  }
}
