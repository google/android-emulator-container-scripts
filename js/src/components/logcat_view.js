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
import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem";
import ListItemText from "@material-ui/core/ListItemText";
import { Logcat } from "android-emulator-webrtc/emulator";
/**
 * A very simple logcat viewer. It displays all logcat items in a material list.
 */
export default class LogcatView extends Component {
  state = { lines: [] };

  static propTypes = {
    uri: PropTypes.string, // grpc endpoint
    auth: PropTypes.object, // auth module to use.
    maxHistory: PropTypes.number
  };

  static defaultProps = {
    maxHistory: 2048 // Max nr of bytes.
  };
  constructor(props) {
    super(props);
    const { uri, auth } = this.props;
    this.buffer = ""
    this.logcat = new Logcat(uri, auth);
  }

  componentDidMount = () => {
    this.logcat.start(this.onLogcat, 1000);
  };

  componentWillUnmount = () => {
    this.logcat.stop();
  };

  onLogcat = logline => {
    const  { maxHistory } = this.props
    this.buffer += logline;
    const sliceAt = this.buffer.length - maxHistory
    if (sliceAt > 0) {
      this.buffer = this.buffer.substr(this.buffer.indexOf('\n', sliceAt));
    }
    this.setState({ lines: this.buffer.split('\n') });
  };

  asItems = loglines => {
    var i = 0;
    return loglines.map(line => (
      <ListItem key={i++}>
        <ListItemText primary={line} />
      </ListItem>
    ));
  };

  render() {
    const { lines } = this.state;
    return <List dense={true}>{this.asItems(lines)}</List>;
  }
}
