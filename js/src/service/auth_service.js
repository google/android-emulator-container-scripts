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

/**
 * A TokenHolder that holds a JWT token.
 *
 * @export
 * @class TokenAuthService
 */
export class TokenProviderService {
  /**
   *Creates an instance of TokenAuthService.
   * @param {string} uri The endpoint that hands out a JWT Token.
   * @memberof TokenAuthService
   */
  constructor() {
    this.events = new EventEmitter();
    this.token = null;
  }

  setToken = (token) => {
    this.token = token;
    this.events.emit("authorized", true);
  }

  /**
   * Get notifications for state changes.
   * Currently only `authorized` is supported.
   *
   * @param {string} name of the event
   * @param {callback} fn To be invoked
   */
  on = (name, fn) => {
    this.events.on(name, fn);
  };


  /**
   * Logs the user out by resetting the token.
   *
   * @returns A promis
   */
  logout = () => {
    return new Promise((resolve, reject) => {
      this.token = null;
      resolve(null);
      this.events.emit("authorized", false);
    });
  };

  /**
   * Called by the EmulatorWebClient when the web endpoint
   * returns a 401. It will fire the `authorized` event.
   *
   * @memberof TokenAuthService
   * @see EmulatorWebClient
   */
  unauthorized = ev => {
    this.token = null;
    this.events.emit("authorized", false);
  };

  /**
   *
   * @memberof TokenAuthService
   * @returns True if a token is set.
   */
  authorized = () => {
    return this.token != null;
  };

  /**
   * Called by the EmulatorWebClient to obtain the authentication
   * headers
   *
   * @memberof TokenAuthService
   * @returns The authentication header for the web call
   * @see EmulatorWebClient
   */
  authHeader = () => {
    return { Authorization: this.token };
  };
}
