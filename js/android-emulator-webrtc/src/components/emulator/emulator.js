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
import {
  RtcService,
  EmulatorControllerService
} from "../../proto/emulator_web_client";

const PngView = withMouseKeyHandler(EmulatorPngView);
const RtcView = withMouseKeyHandler(EmulatorWebrtcView);

/**
 * A React component that displays a remote android emulator.
 *
 * The emulator will mount a png or webrtc view component to display the current state
 * of the emulator. It will translate mouse events on this component and send them
 * to the actual emulator.
 *
 * The size of this component will be: width x height
 */
export default class Emulator extends Component {
  static propTypes = {
    uri: PropTypes.string, // endpoint where we can reach the emulator.
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
     * very slow.
     *
     * Note: The pngview does NOT support polling of screenshots and requires
     * the envoy proxy.
     */
    view: PropTypes.oneOf(["webrtc", "png"]).isRequired,
    /** True if polling should be used, only set this to true if you are using the gowebrpc proxy. */
    poll: PropTypes.bool,
    /** Callback that will be invoked in case of gRPC errors. */
    onError: PropTypes.func
  };

  static defaultProps = {
    width: 378,
    height: 672,
    view: "webrtc",
    auth: null,
    poll: false,
    onError: e => {
      console.log(e);
    }
  };

  components = {
    webrtc: RtcView,
    png: PngView
  };

  constructor(props) {
    super(props);
    const { uri, auth, poll } = props;
    this.emulator = new EmulatorControllerService(uri, auth, this.onError);
    this.rtc = new RtcService(uri, auth, this.onError);
    this.jsep = new JsepProtocol(this.emulator, this.rtc, poll);
  }

  render() {
    const { width, height, view } = this.props;
    const SpecificView = this.components[view] || RtcView;
    //const styled = { outline: "none", maxWidth: width * scale };
    return (
      <SpecificView
        width={width}
        height={height}
        emulator={this.emulator}
        jsep={this.jsep}
      />
    );
  }
}
