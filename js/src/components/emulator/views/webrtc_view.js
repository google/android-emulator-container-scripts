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

/**
 * A view on the emulator that is using WebRTC. It will use the Jsep protocol over gRPC to
 * establish the video streams.
 */
export default class EmulatorWebrtcView extends Component {
  static propTypes = {
    emulator: PropTypes.object, // emulator service
    width: PropTypes.number,
    height: PropTypes.number
  };

  static defaultProps = {
    width: 1080,
    height: 1920
  };

  componentDidMount = () => {
    const { emulator } = this.props;
    this.jsep = new JsepProtocolDriver(emulator, this.onConnect);
    this.jsep.startStream();
  };

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

  render() {
    const { width, height } = this.props;
    return (
      <div>
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
