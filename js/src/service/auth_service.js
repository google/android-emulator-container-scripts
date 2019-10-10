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

import PropTypes from "prop-types";
import { Component } from "react";
import axios from "axios";

// An auth service class is responsible for providing an authentication header
// that will be send along with every gRPC request. The auth service must be
// injected in every emulator component with the "auth" property.
//
// The unauthorized(err) method will be invoked whenever a 401 status code is received.
export class TokenAuthService extends Component {
  static propTypes = {
    auth_uri: PropTypes.string.isRequired, // gRPC endpoint of the emulator.
    onLogin: PropTypes.func,
    onLogout: PropTypes.func,
    onRegister: PropTypes.func,
    onUnauthorized: PropTypes.func
  };

  state = {
    token: null
  };

  login = (email, password) => {
    const { onLogin } = this.props;
    return axios
      .get(this.props.auth_uri, {
        auth: {
          username: email,
          password: password
        }
      })
      .then(response => {
        this.state.token = "Bearer " + response.data;
        if (onLogin) {
          onLogin();
        }
      });
  };

  logout = () => {
    const { onLogout } = this.props;
    return new Promise((resolve, reject) => {
      this.state.token = null;
      resolve(null);
      if (onLogout) {
        onLogout();
      }
    });
  };

  unauthorized = ev => {
    console.log("Not authorized: " + ev);
    const { onUnauthorized } = this.props;
    if (onUnauthorized) {
      onUnauthorized();
    }
  };

  register = (email, password) => {
    return new Promise((resolve, reject) => {
      reject(new Error("Register not supported"));
    });
  };

  isLoggedIn = () => {
    const { token } = this.state;
    return token != null;
  };

  authHeader = () => {
    const { token } = this.state;
    return { Authorization: token };
  };
}

// Always logged in and no headers will be set.
export class NoAuthService extends Component {
  static propTypes = {
    auth_uri: PropTypes.string.isRequired, // gRPC endpoint of the emulator.
    onLogin: PropTypes.func,
    onLogout: PropTypes.func,
    onRegister: PropTypes.func,
    onUnauthorized: PropTypes.func
  };

  state = {
    loggedin: false
  };
  login = (email, password) => {
    const { onLogin } = this.props;

    return new Promise((resolve, reject) => {
      this.state.loggedin = true;
      resolve(null);

      if (onLogin) {
        onLogin();
      }
    });
  };

  logout = () => {
    return new Promise((resolve, reject) => {
      this.state.loggedin = false;
      resolve(null);
    });
  };

  register = (email, password) => {
    return new Promise((resolve, reject) => {
      reject(new Error("Register not supported"));
    });
  };

  unauthorized = ev => {
    console.log("Not authorized: " + ev);
  };

  isLoggedIn = () => {
    console.log("Always logged in..");
    return this.state.loggedin;
  };

  authHeader = () => {
    return {};
  };
}
