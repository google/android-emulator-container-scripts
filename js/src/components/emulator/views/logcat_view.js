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
import Logcat from "../net/logcat.js";
import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem";
import ListItemText from "@material-ui/core/ListItemText";
/**
 * A very simple logcat viewer. It displays all logcat items in a material list.
 */
export default class LogcatView extends Component {
  state = { lines: [] };

  static propTypes = {
    emulator: PropTypes.object, // emulator service
    maxHistory: PropTypes.number
  };

  static defaultProps = {
    maxHistory: 64 // Number of loglines to keep.
  };

  componentDidMount = () => {
    const { emulator } = this.props;
    this.buffer = []
    this.logcat = new Logcat(emulator);
    this.logcat.start(this.onLogcat);
  };

  componentWillUnmount = () => {
    this.logcat.stop();
  };

  onLogcat = logline => {
    this.buffer.push(logline)
    if (this.buffer.length > this.props.maxHistory) {
      this.buffer.shift()
    }
    this.setState({ lines: this.buffer });
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
