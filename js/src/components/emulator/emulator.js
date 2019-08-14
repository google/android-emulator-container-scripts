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
import PropTypes from "prop-types"
import React, { Component } from "react"
import * as Device from "../../android_emulation_control/emulator_controller_grpc_web_pb.js"
import * as Proto from "../../android_emulation_control/emulator_controller_pb.js"
import EmulatorPngView from "./views/simple_png_view.js"
import EmulatorWebrtcView from "./views/webrtc_view.js"
import EmulatorFallbackView from "./views/fallback_emulator_view.js"

/**
 * An emulator object that displays the screen and sends mouse events via gRPC.
 *
 * The emulator will mount an EmulatorPngView component to display the current state
 * of the emulator. It will translate mouse events on this component and send them
 * to the actual emulator.
 *
 * The size of this component will be: (width * scale) x (height * scale)
 * The refreshRate will be passed on to the view.
 */
export default class Emulator extends Component {
  state = {
    mouseDown: false, // Current state of mouse
    xpos: 0,
    ypos: 0,
  }

  static propTypes = {
    uri: PropTypes.string.isRequired, // gRPC endpoint of the emulator.
    width: PropTypes.number,
    height: PropTypes.number,
    scale: PropTypes.number,
    refreshRate: PropTypes.number,
    view:  PropTypes.oneOf(['webrtc', 'png', 'fallback']).isRequired,
  }

  static defaultProps = {
    width: 1080, // The width of the emulator display
    height: 1920, // The height of the emulator display
    scale: 0.4, // Scale factor of the emulator image
    refreshRate: 5, // Desired refresh rate.
    view: "webrtc"  // Default view to be used.
  }

   components = {
    webrtc: EmulatorWebrtcView,
    png: EmulatorPngView,
    fallback: EmulatorFallbackView
  };

  componentDidMount() {
    const { uri } = this.props
    this.emulatorService = new Device.EmulatorControllerClient(uri)
  }

  setCoordinates = (down, xp, yp) => {
    // It is totally possible that we send clicks that are offscreen..
    const { width, height, scale } = this.props
    const x = Math.round((xp * width) / (width * scale))
    const y = Math.round((yp * height) / (height * scale))

    // Make the grpc call.
    var request = new Proto.MouseEvent()
    request.setX(x)
    request.setY(y)
    request.setButtons(down ? 1 : 0)
    this.emulatorService.sendMouse(request, {}, function (
      err,
      _response
    ) {
      if (err) {
        console.error(
          "Grpc: " + err.code + ", msg: " + err.message,
          "Emulator:setCoordinates"
        )
      }
    })
  }

  handleKey = e => {
    var request = new Proto.KeyboardEvent()
    request.setKey(e.key)
    this.emulatorService.sendKey(request, {}, function (
      err,
      _response
    ) {
      if (err) {
        console.error(
          "Grpc: " + err.code + ", msg: " + err.message,
          "Emulator:sendKey"
        )
      }
    })
  }

  // Properly handle the mouse events.
  handleMouseDown = e => {
    this.setState({ mouseDown: true })
    const { offsetX, offsetY } = e.nativeEvent
    this.setCoordinates(true, offsetX, offsetY)
  }

  handleMouseUp = e => {
    this.setState({ mouseDown: false })
    const { offsetX, offsetY } = e.nativeEvent
    this.setCoordinates(false, offsetX, offsetY)
  }

  handleMouseMove = e => {
    const { mouseDown } = this.state
    if (!mouseDown) return
    const { offsetX, offsetY } = e.nativeEvent
    this.setCoordinates(true, offsetX, offsetY)
  }

  onLogcat = msg => {
    console.log(msg)
  }

  render() {
    const { width, height, scale, uri, refreshRate, view } = this.props
    const SpecificView = this.components[view];
    console.log("Using: " + SpecificView + " , view: " + view)
    return (
      <div
        tabIndex="1"
        onMouseDown={this.handleMouseDown}
        onMouseMove={this.handleMouseMove}
        onMouseUp={this.handleMouseUp}
        onMouseOut={this.handleMouseUp}
        onKeyDown={this.handleKey}
      >
        <SpecificView
          width={width * scale}
          height={height * scale}
          refreshRate={refreshRate}
          uri={uri}
        />
      </div>
    )
  }
}