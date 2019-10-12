import "./App.css";

import { NoAuthService, TokenAuthService } from "./service/auth_service";
import React, { Component } from "react";

import EmulatorScreen from "./components/emulator_screen";
import LoginPage from "./components/login_page";
import { ThemeProvider } from "@material-ui/styles";

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
      this.auth = new NoAuthService({
        onLogin: () => this.setState({ loggedIn: true }),
        onUnauthorized: () => this.setState({ loggedIn: false })
      });
    } else {
      this.auth = new TokenAuthService({
        auth_uri: EMULATOR_GRPC + "/token",
        onLogin: () => this.setState({ loggedIn: true }),
        onUnauthorized: () => this.setState({ loggedIn: false })
      });
    }

    this.state = {
      loggedIn: this.auth.isLoggedIn()
    };
  }

  render() {
    const { loggedIn } = this.state;
    return (
      <ThemeProvider>
        {loggedIn ? (
          <EmulatorScreen uri={EMULATOR_GRPC} auth={this.auth} />
        ) : (
          <LoginPage auth={this.auth} />
        )}
      </ThemeProvider>
    );
  }
}
