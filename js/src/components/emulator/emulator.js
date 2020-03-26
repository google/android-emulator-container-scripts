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
import EmulatorPngView from "./views/simple_png_view.js";
import EmulatorWebrtcView from "./views/webrtc_view.js";
import withMouseKeyHandler from "./views/event_handler";
import JsepProtocol from "./net/jsep_protocol_driver.js";

const PngView = withMouseKeyHandler(EmulatorPngView);
const RtcView = withMouseKeyHandler(EmulatorWebrtcView);

/**
 * An emulator object that displays the screen and sends mouse events via gRPC.
 *
 * The emulator will mount a png or webrtc view component to display the current state
 * of the emulator. It will translate mouse events on this component and send them
 * to the actual emulator.
 *
 * The size of this component will be: (width * scale) x (height * scale)
 */
export default class Emulator extends Component {
  static propTypes = {
    emulator: PropTypes.object, // emulator service, used to control emulator
    rtc: PropTypes.object, // rtc service, responsible for setting up WebRTC
    width: PropTypes.number,  // The width of the displayed emulator
    height: PropTypes.number, // The height of the displayed emulator
    view: PropTypes.oneOf(["webrtc", "png"]).isRequired
  };

  static defaultProps = {
    width: 378, // The width of the emulator display
    height: 672, // The height of the emulator display
    view: "webrtc" // Default view to be used.
  };

  components = {
    webrtc: RtcView,
    png: PngView
  };

  constructor(props) {
    super(props);
    this.jsep = new JsepProtocol(props.emulator, props.rtc);
  }

  render() {
    const { width, height, view, emulator } = this.props;
    const SpecificView = this.components[view] || RtcView;
    //const styled = { outline: "none", maxWidth: width * scale };
    return (
        <SpecificView
          width={width}
          height={height}
          emulator={emulator}
          jsep={this.jsep}
        />
    );
  }
}
