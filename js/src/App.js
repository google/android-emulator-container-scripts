import "./App.css";

import { NoAuthService, TokenAuthService } from "./service/auth_service";
import React, { Component } from "react";

import EmulatorScreen from "./components/emulator_screen";
import LoginPage from "./components/login_page";
import { EmulatorControllerService } from "./components/emulator/net/emulator_web_client";
import Snackbar from '@material-ui/core/Snackbar';
import Alert from '@material-ui/lab/Alert';

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
    this.emulator = new EmulatorControllerService(EMULATOR_GRPC, this.auth, this.onError);

    this.state = {
      authorized: this.auth.authorized(),
      error_snack: false,
      error_msg: "",
    };
    this.auth.on("authorized", a => {
      this.setState({ authorized: a });
    });
  }

  onError = err =>  {
    this.setState( { error_snack: true, error_msg: "Low level gRPC error: " + JSON.stringify(err) });
  }

  handleClose = e => {
    this.setState({ error_snack: false});
  }

  render() {
    const { authorized, error_snack, error_msg } = this.state;
    return (
      <div>
        {authorized ? (
          <EmulatorScreen emulator={this.emulator} auth={this.auth} />
        ) : (
          <LoginPage auth={this.auth} />
        )}
        <Snackbar open={error_snack} autoHideDuration={6000}>
            <Alert onClose={this.handleClose} severity="error">
              {error_msg}
            </Alert>
        </Snackbar>
      </div>
    );
  }
}
