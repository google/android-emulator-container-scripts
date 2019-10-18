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
import PropTypes from "prop-types";
import React, { Component } from "react";
import * as Proto from "../../android_emulation_control/emulator_controller_pb.js";
import EmulatorPngView from "./views/simple_png_view.js";
import EmulatorWebrtcView from "./views/webrtc_view.js";
import EmulatorFallbackView from "./views/fallback_emulator_view.js";

/**
 * An emulator object that displays the screen and sends mouse events via gRPC.
 *
 * The emulator will mount a png, webrtc or fallback view component to display the current state
 * of the emulator. It will translate mouse events on this component and send them
 * to the actual emulator.
 *
 * The size of this component will be: (width * scale) x (height * scale)
 */
export default class Emulator extends Component {
  state = {
    mouseDown: false, // Current state of mouse
    xpos: 0,
    ypos: 0
  };

  static propTypes = {
    emulator: PropTypes.object, // emulator service
    width: PropTypes.number,
    height: PropTypes.number,
    scale: PropTypes.number,
    refreshRate: PropTypes.number, // Refresh rate to use when falling back to screenshots.
    view: PropTypes.oneOf(["webrtc", "png", "fallback"]).isRequired
  };

  static defaultProps = {
    width: 1080, // The width of the emulator display
    height: 1920, // The height of the emulator display
    scale: 0.35, // Scale factor of the emulator image
    refreshRate: 5, // Desired refresh rate if using screenshots.
    view: "webrtc" // Default view to be used.
  };

  components = {
    webrtc: EmulatorWebrtcView,
    png: EmulatorPngView,
    fallback: EmulatorFallbackView
  };

  setCoordinates = (down, xp, yp) => {
    // It is totally possible that we send clicks that are offscreen..
    const { width, height, scale, emulator } = this.props;
    const x = Math.round((xp * width) / (width * scale));
    const y = Math.round((yp * height) / (height * scale));

    // Make the grpc call.
    var request = new Proto.MouseEvent();
    request.setX(x);
    request.setY(y);
    request.setButtons(down ? 1 : 0);
    emulator.sendMouse(request);
  };

  handleKey = e => {
    const { emulator } = this.props;
    var request = new Proto.KeyboardEvent();
    request.setKey(e.key);
    emulator.sendKey(request);
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
    const { width, height, scale, refreshRate, view, emulator } = this.props;
    const SpecificView = this.components[view];
    const styled = { outline: "none", maxWidth: width * scale };
    return (
      <div
        tabIndex="1"
        onMouseDown={this.handleMouseDown}
        onMouseMove={this.handleMouseMove}
        onMouseUp={this.handleMouseUp}
        onMouseOut={this.handleMouseUp}
        onKeyDown={this.handleKey}
        style={styled}
      >
        <SpecificView
          width={width * scale}
          height={height * scale}
          refreshRate={refreshRate}
          emulator={emulator}
        />
      </div>
    );
  }
}
