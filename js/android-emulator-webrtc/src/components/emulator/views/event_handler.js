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
import React from "react";
import * as Proto from "../../../proto/emulator_controller_pb";
import EmulatorStatus from "../net/emulator_status";

/**
 * A handler that extends a view to send key/mouse events to the emulator.
 * It wraps the inner component in a div, and will use the jsep handler
 * to send key/mouse/touch events over the proper channel.
 *
 * It will translate the mouse events based upon the returned display size of
 * the emulator.
 *
 * You usually want to wrap a EmulatorRtcview, or EmulatorPngView in it.
 */
export default function withMouseKeyHandler(WrappedComponent) {
  return class extends React.Component {
    constructor(props) {
      super(props);
      this.state = {
        deviceHeight: 1920,
        deviceWidth: 1080
      };
      this.handler = React.createRef();
    }

    componentDidMount() {
      this.getScreenSize();
    }

    getScreenSize() {
      const { emulator } = this.props;
      const state = new EmulatorStatus(emulator);
      state.updateStatus(state => {
        this.setState({
          deviceWidth: parseInt(state.hardwareConfig["hw.lcd.width"]) || 1080,
          deviceHeight: parseInt(state.hardwareConfig["hw.lcd.height"]) || 1920
        });
      });
    }

    onContextMenu = e => {
      e.preventDefault();
    };

    setCoordinates = (down, xp, yp) => {
      // It is totally possible that we send clicks that are offscreen..
      const { deviceWidth, deviceHeight } = this.state;
      const { clientHeight, clientWidth } = this.handler.current;
      const scaleX = deviceWidth / clientWidth;
      const scaleY = deviceHeight / clientHeight;
      const x = Math.round(xp * scaleX);
      const y = Math.round(yp * scaleY);

      // Forward the request to the jsep engine.
      var request = new Proto.MouseEvent();
      request.setX(x);
      request.setY(y);
      request.setButtons(down ? 1 : 0);

      const { jsep } = this.props;
      jsep.send("mouse", request);
    };

    handleKeyDown = e => {
      var request = new Proto.KeyboardEvent();
      request.setKey(e.key);
      request.setEventtype(2);

      const { jsep } = this.props;
      jsep.send("keyboard", request);
    };

    // Properly handle the mouse events.
    handleMouseDown = e => {
      this.setState({ mouseDown: true });
      const { offsetX, offsetY } = e.nativeEvent;
      this.setCoordinates(true, offsetX, offsetY);
    };

    handleMouseUp = e => {
      this.setState({ mouseDown: false });
      const { offsetX, offsetY } = e.nativeEvent;
      this.setCoordinates(false, offsetX, offsetY);
    };

    handleMouseMove = e => {
      const { mouseDown } = this.state;
      if (!mouseDown) return;
      const { offsetX, offsetY } = e.nativeEvent;
      this.setCoordinates(true, offsetX, offsetY);
    };

    preventDragHandler = e => {
      e.preventDefault();
    };

    render() {
      return (
        <div /* handle interaction */
          onMouseDown={this.handleMouseDown}
          onMouseMove={this.handleMouseMove}
          onMouseUp={this.handleMouseUp}
          onMouseOut={this.handleMouseUp}
          onKeyDown={this.handleKeyDown}
          onDragStart={this.preventDragHandler}
          tabIndex="0"
          ref={this.handler}
          style={{
            pointerEvents: "all",
            outline: "none",
            margin: "0",
            padding: "0",
            border: "0",
            display: "inline-block"
          }}
        >
          <WrappedComponent {...this.props} />
        </div>
      );
    }
  };
}
