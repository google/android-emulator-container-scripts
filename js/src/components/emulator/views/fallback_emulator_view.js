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
import EmulatorPngView from "./simple_png_view.js";
import JsepProtocolDriver from "../net/jsep_protocol_driver.js";

/**
 * A View that will use WebRTC if possible, and otherwise will revert to
 * using the png view.
 */
export default class EmulatorFallbackView extends Component {
  static propTypes = {
    emulator: PropTypes.object, // emulator service
    width: PropTypes.number,
    height: PropTypes.number,
    refreshRate: PropTypes.number
  };

  static defaultProps = {
    width: 1080,
    height: 1920,
    refreshRate: 1
  };

  state = {
    fallback: true
  };

  componentDidMount = () => {
    this.jsep = new JsepProtocolDriver(
      this.props.emulator,
      this.onConnect,
      this.onDisconnect
    );
    this.jsep.startStream();
  };

  onDisconnect = () => {
    this.setState({ fallback: true });
  };

  onConnect = stream => {
    this.setState({ fallback: false }, () => {
      console.log(
        "Connecting video stream: " + this.video + ":" + this.video.readyState
      );
      this.video.srcObject = stream;
      this.video.play();
    });
  };

  onCanPlay = e => {
    console.log("Playing video stream.");
    this.video.play().catch(error => {
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

  render() {
    const { width, height, emulator, refreshRate } = this.props;
    const { fallback } = this.state;
    return (
      <div>
        {!fallback && (
          <video
            ref={node => (this.video = node)}
            width={width}
            height={height}
            onContextMenu={this.onContextMenu}
            onCanPlay={this.onCanPlay}
            muted="muted"
          />
        )}
        {fallback && (
          <EmulatorPngView
            emulator={emulator}
            refreshRate={refreshRate}
            width={width}
            height={height}
          />
        )}
      </div>
    );
  }
}
