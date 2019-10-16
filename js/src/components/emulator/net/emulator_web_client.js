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
import { EmulatorControllerClient } from "../../../android_emulation_control/emulator_controller_grpc_web_pb.js";
import { GrpcWebClientBase } from "grpc-web";
import { EventEmitter } from "events";

class NopAuthenticator {
  authHeader = () => {
    return {};
  };

  unauthorized = () => {};
}

/**
 * A GrcpWebClientBase that inject authentication headers and intercepts
 * errors. If the errors are 401, the unauthorized method of the authenticator will be invoked.
 *
 * @export
 * @class EmulatorWebClient
 * @extends {GrpcWebClientBase}
 */
class EmulatorWebClient extends GrpcWebClientBase {
  constructor(options, auth) {
    super(options);
    this.auth = auth;
    this.events = new EventEmitter();
  }

  on = (name, fn) => {
    this.events.on(name, fn);
  };

  rpcCall = (method, request, metadata, methodinfo, callback) => {
    const authHeader = this.auth.authHeader();
    const meta = { ...metadata, ...authHeader };
    const self = this;
    return super.rpcCall(method, request, meta, methodinfo, (err, res) => {
      if (err) {
        if (err.code === 401) self.auth.unauthorized();
        self.events.emit("error", err);
      }
      if (callback) callback(err, res);
    });
  };

  serverStreaming = (method, request, metadata, methodInfo) => {
    const authHeader = this.auth.authHeader();
    const meta = { ...metadata, ...authHeader };
    const stream = super.serverStreaming(method, request, meta, methodInfo);
    const self = this;

    // Intercept errors.
    stream.on("error", e => {
      if (e.code === 401) {
        self.auth.unauthorized();
      }
      self.events.emit("error", e);
    });
    return stream;
  };
}

/**
 * An EmulatorControllerService is an EmulatorControllerClient that inject authentication headers. 
 * You can provide your own authenticator service that must implement the following mehtods:
 *
 * - `authHeader()` which must return a set of headers that should be send along with a request.
 * - `unauthorized()` a function that gets called when a 401 was received.
 *
 * You can use this to simplify handling authentication failures.
 *
 * TODO(jansene): Maybe expose error handling? That way it does
 * not have to be repeated at every function call.
 *
 * @export
 * @class EmulatorControllerService
 * @extends {EmulatorControllerClient}
 */
export class EmulatorControllerService extends EmulatorControllerClient {
  /**
   *Creates an instance of EmulatorControllerService.
   * @param {string} uri of the emulator controller endpoint.
   * @param {Authenticator} authenticator used to authenticate with the emulator endpoint.
   * @memberof EmulatorControllerService
   */
  constructor(uri, authenticator) {
    super(uri);
    if (!authenticator) authenticator = new NopAuthenticator();
    this.client_ = new EmulatorWebClient({}, authenticator);
  }
}
