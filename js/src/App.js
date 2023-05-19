import "./App.css";

import { TokenProviderService } from "./service/auth_service";
import React, { Component } from "react";

import EmulatorScreen from "./components/emulator_screen";
import LoginPage from "./components/login_firebase";

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
    this.auth = new TokenProviderService();
    this.state = {
      authorized: this.auth.authorized(),
    };
this.auth.on("authorized", a => {
      this.setState({ authorized: a });
    });
  }


  render() {
    const { authorized } = this.state;
    console.log(`Authorized: ${authorized}`);
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
