import "./App.css";

import { NoAuthService, TokenAuthService } from "./service/auth_service";
import React, { Component } from "react";

import EmulatorScreen from "./components/emulator_screen";
import LoginPage from "./components/login_page";

const development =
  !process.env.NODE_ENV || process.env.NODE_ENV === "development";

var EMULATOR_GRPC =
  window.location.protocol +
  "//" +
  window.location.hostname +
  ":" +
  window.location.port;
if (development) {
  EMULATOR_GRPC =  window.location.protocol + "//" +
  window.location.hostname + ":8080";
}

export default class App extends Component {
  constructor(props) {
    super(props);
    if (development) {
      this.auth = new NoAuthService();
    } else {
      this.auth = new TokenAuthService(EMULATOR_GRPC + "/token");
    }

    this.state = {
      authorized: this.auth.authorized(),
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
          <EmulatorScreen uri={EMULATOR_GRPC} auth={this.auth} />
        ) : (
          <LoginPage auth={this.auth} />
        )}
      </div>
    );
  }
}
