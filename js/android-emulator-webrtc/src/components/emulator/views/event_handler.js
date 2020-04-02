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
        deviceWidth: 1080,
        mouse: {
          xp: 0,
          yp: 0,
          mouseDown: false, // Current state of mouse
          // Current button pressed.
          // In proto, 0 is "no button", 1 is left, and 2 is right.
          mouseButton: 0
        }
      };
      this.handler = React.createRef();
      const { emulator } = this.props;
      this.status = new EmulatorStatus(emulator);
    }

    componentDidMount() {
      this.getScreenSize();
    }

    getScreenSize() {
      this.status.updateStatus(state => {
        this.setState({
          deviceWidth: parseInt(state.hardwareConfig["hw.lcd.width"]) || 1080,
          deviceHeight: parseInt(state.hardwareConfig["hw.lcd.height"]) || 1920
        });
      });
    }

    onContextMenu = e => {
      e.preventDefault();
    };

    setCoordinates = () => {
      // It is totally possible that we send clicks that are offscreen..
      const { deviceWidth, deviceHeight } = this.state;
      const { mouseDown, mouseButton, xp, yp } = this.state.mouse;
      const { clientHeight, clientWidth } = this.handler.current;
      const scaleX = deviceWidth / clientWidth;
      const scaleY = deviceHeight / clientHeight;
      const x = Math.round(xp * scaleX);
      const y = Math.round(yp * scaleY);

      if (isNaN(x) || isNaN(y)) {
        console.log("Ignoring: x: " + x + ", y:" + y);
        return;
      }

      // Forward the request to the jsep engine.
      var request = new Proto.MouseEvent();
      request.setX(x);
      request.setY(y);
      request.setButtons(mouseDown ? mouseButton : 0);
      const { jsep } = this.props;
      jsep.send("mouse", request);
    };

    handleKey = eventType => {
      return e => {
        var request = new Proto.KeyboardEvent();
        request.setEventtype(
          eventType === "KEYDOWN"
            ? Proto.KeyboardEvent.KeyEventType.KEYDOWN
            : eventType === "KEYUP"
            ? Proto.KeyboardEvent.KeyEventType.KEYUP
            : Proto.KeyboardEvent.KeyEventType.KEYPRESS
        );
        request.setKey(e.key);
        const { jsep } = this.props;
        jsep.send("keyboard", request);
      };
    };

    // Properly handle the mouse events.
    handleMouseDown = e => {
      const { offsetX, offsetY } = e.nativeEvent;
      this.setState(
        {
          mouse: {
            xp: offsetX,
            yp: offsetY,
            mouseDown: true,
            // In browser's MouseEvent.button property,
            // 0 stands for left button and 2 stands for right button.
            mouseButton: e.button === 0 ? 1 : e.button === 2 ? 2 : 0
          }
        },
        this.setCoordinates
      );
    };

    handleMouseUp = e => {
      const { offsetX, offsetY } = e.nativeEvent;
      this.setState(
        {
          mouse: { xp: offsetX, yp: offsetY, mouseDown: false, mouseButton: 0 }
        },
        this.setCoordinates
      );
    };

    handleMouseMove = e => {
      // Let's not overload the endpoint with useless events.
      if (!this.state.mouse.mouseDown)
        return;

      const { offsetX, offsetY } = e.nativeEvent;
      var mouse = this.state.mouse;
      mouse.xp = offsetX;
      mouse.yp = offsetY;
      this.setState({ mouse: mouse }, this.setCoordinates);
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
          onKeyDown={this.handleKey("KEYDOWN")}
          onKeyUp={this.handleKey("KEYUP")}
          onDragStart={this.preventDragHandler}
          tabIndex="0"
          ref={this.handler}
          style={{
            pointerEvents: "all",
            outline: "none",
            margin: "0",
            padding: "0",
            border: "0",
            display: "inline-block",
            width: "100%"
          }}
        >
          <WrappedComponent {...this.props} />
        </div>
      );
    }
  };
}
