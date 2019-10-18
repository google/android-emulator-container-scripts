import "./App.css";

import { NoAuthService, TokenAuthService } from "./service/auth_service";
import React, { Component } from "react";

import EmulatorScreen from "./components/emulator_screen";
import LoginPage from "./components/login_page";
import { EmulatorControllerService } from "./components/emulator/net/emulator_web_client";

const development =
  !process.env.NODE_ENV || process.env.NODE_ENV === "development";

var EMULATOR_GRPC =
  window.location.protocol +
  "//" +
  window.location.hostname +
  ":" +
  window.location.port;
if (development) {
  EMULATOR_GRPC = "http://localhost:8080";
}

export default class App extends Component {
  constructor(props) {
    super(props);
    if (development) {
      this.auth = new NoAuthService();
    } else {
      this.auth = new TokenAuthService(EMULATOR_GRPC + "/token");
    }
    this.emulator = new EmulatorControllerService(EMULATOR_GRPC, this.auth);
    this.state = {
      authorized: this.auth.authorized()
    };
    this.auth.on("authorized", a => {
      this.setState({ authorized: a });
    });
  }

  render() {
    const { authorized } = this.state;
    return (
      <div>
        {authorized ? (
          <EmulatorScreen emulator={this.emulator} auth={this.auth} />
        ) : (
          <LoginPage auth={this.auth} />
        )}
      </div>
    );
  }
}
