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
 * Gets the logcat stream from the emulator. Register for the 'data' event to receive a logline
 * when one is available.
 *
 * This requires streaming and will not work with the go grpc webproxy.
 *
 * @export
 * @class Logcat
 */
export default class Logcat {
  /**
   * Creates a logcat stream.
   *
   * @param {object} uriOrEmulator An emulator controller service, or a URI to a gRPC endpoint.
   * @param {object} auth The authentication service to use, or null for no authentication.
   *
   *  The authentication service should implement the following methods:
   * - `authHeader()` which must return a set of headers that should be send along with a request.
   * - `unauthorized()` a function that gets called when a 401 was received.
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
  }

  on = (name, fn) => {
    this.events.on(name, fn);
  };

  /**
   * Stops the ongoing stream by canceling it. This will raise an error.
   *
   * @memberof Logcat
   */
  stop = () => {
    if (this.stream) {
      this.stream.cancel();
    }
  };

  /**
   * Requests the logcat stream.
   *
   * @param  {Callback} fnNotify when a new log line arrives.
   * @memberof Logcat
   */
  start = fnNotify => {
    if (fnNotify) this.on("data", fnNotify);
    const self = this;
    /* eslint-disable */
    const request = new proto.android.emulation.control.LogMessage();
    request.setStart(this.offset);
    this.stream = this.emulator.streamLogcat(request);

    this.stream.on("data", response => {
      self.offset = response.getNext();
      const contents = response.getContents();
      const lines = contents.split("\n");
      const last = contents[contents.length - 1];
      var cnt = lines.length;
      if (last != "\n") {
        cnt--;
        self.lastline += lines[Math.max(0, cnt - 1)];
      }
      for (var i = 0; i < cnt; i++) {
        var line = lines[i];
        if (i === 0) {
          line = self.lastline + line;
          self.lastline = "";
        }
        if (line.length > 0) self.events.emit("data", line);
      }
    });
    this.stream.on("error", error => {
      if ((error.code = 1)) {
        // Ignore we got cancelled.
      }
    });
  };
}
