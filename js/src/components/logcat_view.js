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
import { Logcat } from "android-emulator-webrtc/emulator";
import { LazyLog, ScrollFollow } from "react-lazylog";
import { EventEmitter } from "events";

/**
 * A logcat viewer using a modified mozilla react lazy log.
 */
export default class LogcatView extends Component {
  state = { lines: [] };

  static propTypes = {
    uri: PropTypes.string, // grpc endpoint
    auth: PropTypes.object, // auth module to use.
  };

  constructor(props) {
    super(props);
    const { uri, auth } = this.props;
    this.logcat = new Logcat(uri, auth);
    this.emitter = new EventEmitter();
    this.emitter.on("start", () => {
      this.logcat.start(this.onLogcat);
      this.emitter.emit("data", "Starting logcat.\n");
    });
    this.emitter.on("abort", () => {
      this.logcat.stop();
    });
  }

  onLogcat = (loglines) => {
    this.emitter.emit("data", loglines);
  };

  render() {
    return (
      <ScrollFollow
        startFollowing
        render={({ onScroll, follow, startFollowing, stopFollowing }) => (
          <LazyLog
            extraLines={1}
            enableSearch
            eventSource={this.emitter}
            onScroll={onScroll}
            follow={follow}
          />
        )}
      />
    );
  }
}
