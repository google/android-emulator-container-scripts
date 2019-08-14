/**
 * @fileoverview Description of this file.
 */
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
import * as Device from "../../../android_emulation_control/emulator_controller_grpc_web_pb.js";

/**
 * This pulls the logcat stream from the Emulator, it is basically an invisible React component.
 * Register the onMessage callback to get events when new log messages are coming in.
 */
export default class Logcat extends Component {

    constructor() {
        super()
    }

    static propTypes = {
        uri: PropTypes.string.isRequired, // gRPC endpoint of the emulator
        onMessage: PropTypes.func, // Callback logcat lines are coming in
    };

    static defaultProps = {
        onLogcat: function () { },
        refreshRate: 1000, // Once every second.
    }

    state = {
        offset: 0, // Current offset, we will be query point
        lastline: ""
    };

    componentDidMount() {
        const { uri, refreshRate } = this.props;
        this.emulatorService = new Device.EmulatorControllerClient(uri);
        this.updateLog()
        this.timerID = setInterval(
            () => this.updateLog(),
            refreshRate
        );
    }

    componentWillUnmount() {
        clearInterval(this.timerID);
    }

    /* Makes a grpc call to get a screenshot */
    updateLog() {
        /* eslint-disable */
        const { offset } = this.state
        const self = this;
        var request = new proto.android.emulation.control.LogMessage()
        request.setStart(offset)
        var call = this.emulatorService.getLogcat(request, {}, function (
            err,
            response
        ) {
            if (!err) {
                const { onLogcat } = self.props
                const { lastline } = self.state
                // Update the image with the one we just received.
                if (response.getNext())
                    self.setState({ offset: response.getNext() })

                var contents = response.getContents()
                var lines = contents.split('\n')
                lines[0] = lastline + lines[0]
                if (!contents[contents.length - 1] != '\n') {
                    // Partial line.
                    self.setState({ lastline: lines.pop() })

                }
                onLogcat(lines)
            }
        });
    }

    render() {
        return null
    }
}
