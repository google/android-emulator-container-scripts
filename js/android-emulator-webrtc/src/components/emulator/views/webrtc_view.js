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

/**
 * A view on the emulator that is using WebRTC. It will use the Jsep protocol over gRPC to
 * establish the video streams.
 */
export default class EmulatorWebrtcView extends Component {
  static propTypes = {
    /** Jsep protocol driver, used to establish the video stream. */
    jsep: PropTypes.object
  };

  constructor(props) {
    super(props);
    this.video = React.createRef();
  }

  componentWillUnmount = () => {
    this.props.jsep.disconnect();
  };

  componentDidMount = () => {
    this.props.jsep.on("connected", this.onConnect);
    this.props.jsep.startStream();
  };

  onConnect = stream => {
    const video = this.video.current;
    if (!video) {
      // Component was unmounted.
      return;
    }
    console.log("Connecting video stream: " + video + ":" + video.readyState);
    video.srcObject = stream;
    // Kick off playing in case we already have enough data available.
    video.play();
  };

  onCanPlay = e => {
    const video = this.video.current;
    if (!video) {
      // Component was unmounted.
      return;
    }

    video
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
    return (
      <video
        ref={this.video}
        style={{
        display: "block",
        position: "relative",
        width: "100%",
        height: "100%",
        objectFit: "contain",
        objectPosition: "center"
      }}
        muted="muted"
        onContextMenu={this.onContextMenu}
        onCanPlay={this.onCanPlay}
      />
    );
  }
}
