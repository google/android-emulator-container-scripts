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
 * A very simple logcat viewer. TIt displays all logcat items in a material list.
 */
class LogcatView extends Component {
  state = { lines: [] };

  static propTypes = {
    uri: PropTypes.string.isRequired, // gRPC endpoint of the emulator.
    auth: PropTypes.func.isRequired, // Auth service
    refreshRate: PropTypes.number,
    maxHistory: PropTypes.number,
    classes: PropTypes.object.isRequired
  };

  static defaultProps = {
    refreshRate: 1000, // Desired refresh rate.
    maxHistory: 512 // Number of loglines to keep.
  };

  onLogcat = loglines => {
    const { lines } = this.state;
    const { maxHistory } = this.props;
    var newLines = lines.concat(loglines);
    if (newLines.length > maxHistory) {
      newLines = newLines.splice(newLines.length - maxHistory);
    }

    this.setState({ lines: newLines });
  };

  asItems = loglines => {
    return loglines.map(line => (
      <ListItem>
        <ListItemText primary={line} />
      </ListItem>
    ));
  };

  render() {
    const { lines } = this.state;
    const { auth, uri } = this.props;
    return (
      <List dense="true">
        {this.asItems(lines)}
        <Logcat uri={uri} auth={auth} onLogcat={this.onLogcat} />
      </List>
    );
  }
}

export default LogcatView;
