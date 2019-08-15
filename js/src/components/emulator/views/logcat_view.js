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
import PropTypes from 'prop-types';
import React, { Component } from 'react';
import Logcat from '../net/logcat.js'

/**
 * A very simple logcat viewer.
 */
class LogcatView extends Component {
    state = { lines: [] }

    static propTypes = {
        uri: PropTypes.string.isRequired,  // gRPC endpoint of the emulator.
        refreshRate: PropTypes.number,
        maxHistory: PropTypes.number,
        classes: PropTypes.object.isRequired
    }

    static defaultProps = {
        refreshRate: 1000,  // Desired refresh rate.
        maxHistory: 512    // Number of loglines to keep.
    }

    onLogcat = loglines => {
        const { lines } = this.state
        const { maxHistory } = this.props
        var newLines = lines.concat(loglines)
        if (newLines.length > maxHistory) {
            newLines = newLines.splice(newLines.length - maxHistory)
        }

        this.setState({ lines: newLines })
    }

    asItems = loglines => {
        return loglines.map(line => (<p>{line}</p>))
    }

    render() {
        const { lines } = this.state
        const { classes } = this.props;
        return (
            <div>
                <Logcat uri={this.props.uri} onLogcat={this.onLogcat} />
                {this.asItems(lines)}
            </div>
        )
    }
}

export default LogcatView;
