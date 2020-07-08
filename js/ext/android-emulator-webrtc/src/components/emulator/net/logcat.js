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
import { EventEmitter } from "events";
import "../../../proto/emulator_controller_pb";
import { EmulatorControllerService } from "../../../proto/emulator_web_client";

/**
 * Observe the logcat stream from the emulator.
 *
 * This requires server side streaming and will only work with the envoy proxy.
 */
export default class Logcat {
  /**
   * Creates a logcat stream.
   *
   *  The authentication service should implement the following methods:
   * - `authHeader()` which must return a set of headers that should be send along with a request.
   * - `unauthorized()` a function that gets called when a 401 was received.
   *
   * @constructor
   * @param {object} uriOrEmulator
   * @param {object} auth
   */
  constructor(uriOrEmulator, auth) {
    if (uriOrEmulator instanceof EmulatorControllerService) {
      this.emulator = uriOrEmulator;
    } else {
      this.emulator = new EmulatorControllerService(uriOrEmulator, auth);
    }
    this.offset = 0;
    this.lastline = "";
    this.events = new EventEmitter();
    this.stream = null;
    this.poll = false;
  }

  /**
   * Register a listener.
   *
   * @param {string} name Name of the event.
   * @param  {Callback} fn Function to notify on the given event.
   * @memberof Logcat
   */
  on = (name, fn) => {
    this.events.on(name, fn);
  };

  /**
   * Removes a listener.
   *
   * @param {string} name Name of the event.
   * @param  {Callback} fn Function to notify on the given event.
   * @memberof Logcat
   */
  off = (name, fn) => {
    this.events.off(name, fn);
  };

  /**
   * Cancel the currently active logcat stream.
   *
   * @memberof Logcat
   */
  stop = () => {
    if (this.stream) {
      this.stream.cancel();
    }
    this.poll = false;
  };

  pollStream = () => {
    const self = this;
    /* eslint-disable */
    const request = new proto.android.emulation.control.LogMessage();
    request.setStart(this.offset);
    this.emulator.getLogcat(request, {}, (err, response) => {
      self.offset = response.getNext();
      const contents = response.getContents();
      self.events.emit("data", contents);
      if (this.poll) {
        self.pollStream();
      }
    });
  };

  // Uses streaming, this really locks up the ui, so best not to use for now.
  stream = () => {
    const self = this;
    /* eslint-disable */
    const request = new proto.android.emulation.control.LogMessage();
    request.setStart(this.offset);
    this.stream = this.emulator.streamLogcat(request);
    this.stream.on("data", (response) => {
      self.offset = response.getNext();
      const contents = response.getContents();
      self.events.emit("data", contents);
    });
    this.stream.on("error", (error) => {
      if ((error.code = 1)) {
        // Ignore we got cancelled.
      }
    });
  };

  /**
   * Requests the logcat stream, invoking the callback when a log line arrives.
   *
   * @param  {Callback} fnNotify when a new log line arrives.
   * @memberof Logcat
   */
  start = (fnNotify) => {
    if (fnNotify) this.on("data", fnNotify);
    this.poll = true;
    this.pollStream();
  };
}
