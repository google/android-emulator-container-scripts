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
import axios from "axios";
import { EventEmitter } from "events";

/**
 * A TokenAuthService is an authentication service that can login
 * using BasicAuth to an endpoint to obtain a JWT token.
 * This JWT token will be set on the header for every outgoing request.
 *
 * @export
 * @class TokenAuthService
 */
export class TokenAuthService {
  /**
   *Creates an instance of TokenAuthService.
   * @param {string} uri The endpoint that hands out a JWT Token.
   * @memberof TokenAuthService
   */
  constructor(uri) {
    this.events = new EventEmitter();
    this.auth_uri = uri;
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
   * Obtains a JWT token with basic auth for the given username and password.
   *
   * @param {string} email The user name/email
   * @param {string} password The password
   * @returns A promise
   */
  login = (email, password) => {
    return axios
      .get(this.auth_uri, {
        auth: {
          username: email,
          password: password
        }
      })
      .then(response => {
        this.token = "Bearer " + response.data;
        this.events.emit("authorized", true);
      });
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

  register = (email, password) => {
    return new Promise((resolve, reject) => {
      reject(new Error("Register not supported"));
    });
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

/**
 * An authentication service that can be used for testing.
 * It will declare itself logged in as soon as the login method has been invoked.
 *
 * @export
 * @class NoAuthService
 */
export class NoAuthService {
  constructor() {
    this.events = new EventEmitter();
    this.loggedin = true;
  }

  on = (name, fn) => {
    this.events.on(name, fn);
  };

  login = (email, password) => {
    return new Promise((resolve, reject) => {
      this.loggedin = true;
      resolve(null);
      this.events.emit("authorized", this.loggedin);
    });
  };

  logout = () => {
    return new Promise((resolve, reject) => {
      this.loggedin = false;
      resolve(null);
      this.events.emit("authorized", this.loggedin);
    });
  };

  register = (email, password) => {
    return new Promise((resolve, reject) => {
      reject(new Error("Register not supported"));
    });
  };

  unauthorized = ev => {
    this.loggedin = false;
    this.events.emit("authorized", this.loggedin);
  };

  authorized = () => {
    return this.loggedin;
  };

  authHeader = () => {
    return {};
  };
}
