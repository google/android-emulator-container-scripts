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
import JsepProtocolDriver from "../net/jsep_protocol_driver.js";
import * as Proto from "../../../android_emulation_control/emulator_controller_pb.js";
import EmulatorStatus from "../net/emulator_status";

/**
 * A view on the emulator that is using WebRTC. It will use the Jsep protocol over gRPC to
 * establish the video streams. Mouse & key events will be send of data channels.
 */
export default class EmulatorWebrtcView extends Component {
  static propTypes = {
    rtc: PropTypes.object, // rtc service
    emulator: PropTypes.object, // emulator service
    width: PropTypes.number,
    height: PropTypes.number
  };

  state = {
    mouseDown: false, // Current state of mouse
    deviceWidth: 1080,
    deviceHeight: 1920
  };

  componentWillUnmount = () => {
    this.jsep.disconnect();
  };

  componentDidMount = () => {
    this.getScreenSize();
    const { rtc } = this.props;
    this.jsep = new JsepProtocolDriver(rtc, this.onConnect);
    this.jsep.startStream();
  };

  getScreenSize() {
    const { emulator } = this.props;
    const state = new EmulatorStatus(emulator);
    state.updateStatus(state => {
      this.setState({
        deviceWidth: parseInt(state.hardwareConfig["hw.lcd.width"]) || 1080,
        deviceHeight: parseInt(state.hardwareConfig["hw.lcd.height"]) || 1920
      });
    });
  }

  onConnect = stream => {
    console.log(
      "Connecting video stream: " + this.video + ":" + this.video.readyState
    );
    this.video.srcObject = stream;
    // Kick off playing in case we already have enough data available.
    this.video.play();
  };

  onCanPlay = e => {
    this.video
      .play()
      .then(_ => {
        console.log("Automatic playback started!");
      })
      .catch(error => {
        // Autoplay is likely disabled in chrome
        // https://developers.google.com/web/updates/2017/09/autoplay-policy-changes
        // so we should probably show something useful here.
        // We explicitly set the video stream to muted, so this shouldn't happen,
        // but is something you will have to fix once enabling audio.
        alert(
          "code: " +
            error.code +
            ", msg: " +
            error.message +
            ", name: " +
            error.nane
        );
      });
  };

  onContextMenu = e => {
    e.preventDefault();
  };

  setCoordinates = (down, xp, yp) => {
    // It is totally possible that we send clicks that are offscreen..
    const { deviceWidth, deviceHeight } = this.state;
    const elemHeight = this.video.clientHeight;
    const elemWidth = this.video.clientWidth;
    const scaleX = deviceWidth / elemWidth;
    const scaleY = deviceHeight / elemHeight;
    const x = Math.round(xp * scaleX);
    const y = Math.round(yp * scaleY);

    // Forward the request to the jsep engine.
    var request = new Proto.MouseEvent();
    request.setX(x);
    request.setY(y);
    request.setButtons(down ? 1 : 0);
    this.jsep.send("mouse", request);
  };

  handleKeyDown = e => {
    var request = new Proto.KeyboardEvent();
    request.setKey(e.key);
    request.setEventtype(2);
    this.jsep.send("keyboard", request);
  };

  // Properly handle the mouse events.
  handleMouseDown = e => {
    this.setState({ mouseDown: true });
    const { offsetX, offsetY } = e.nativeEvent;
    this.setCoordinates(true, offsetX, offsetY);
  };

  handleMouseUp = e => {
    this.setState({ mouseDown: false });
    const { offsetX, offsetY } = e.nativeEvent;
    this.setCoordinates(false, offsetX, offsetY);
  };

  handleMouseMove = e => {
    const { mouseDown } = this.state;
    if (!mouseDown) return;
    const { offsetX, offsetY } = e.nativeEvent;
    this.setCoordinates(true, offsetX, offsetY);
  };

  render() {
    const { width, height } = this.props;
    return (
      <div
        /* handle interaction */
        onMouseDown={this.handleMouseDown}
        onMouseMove={this.handleMouseMove}
        onMouseUp={this.handleMouseUp}
        onMouseOut={this.handleMouseUp}
        onKeyDown={this.handleKeyDown}
        tabIndex="0"
      >
        <video
          ref={node => (this.video = node)}
          width={width}
          height={height}
          muted="muted"
          onContextMenu={this.onContextMenu}
          onCanPlay={this.onCanPlay}
        />
      </div>
    );
  }
}
