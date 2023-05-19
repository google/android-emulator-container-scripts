import React, { useState, useEffect } from "react";
import { TokenProviderService } from "./service/auth_service";
import EmulatorScreen from "./components/emulator_screen";
import LoginPage from "./components/login_firebase";
import { ThemeProvider,  makeStyles } from '@mui/styles';
import { createTheme } from '@mui/material/styles';

import "./App.css";

const development =
  !process.env.NODE_ENV || process.env.NODE_ENV === "development";

var EMULATOR_GRPC =
  window.location.protocol +
  "//" +
  window.location.hostname +
  ":" +
  window.location.port;
if (development) {
  EMULATOR_GRPC = window.location.protocol + "//" +
    window.location.hostname + ":8080";
}


console.log(`Connecting to grpc at ${EMULATOR_GRPC}`);

const useStyles = makeStyles((theme) => ({
  root: {
    // some CSS that accesses the theme
  }
}));

const theme = createTheme({

});

const auth = new TokenProviderService();

export default function App() {
  const [authorized, setAuthorized] = useState(false);

  useEffect(() => {
    const handleAuthorization = (a) => {
      setAuthorized(a);
    };

    auth.on("authorized", handleAuthorization);
  }, []);


  return (
    <ThemeProvider theme={theme}>
      {authorized ? (
        <EmulatorScreen uri={EMULATOR_GRPC} auth={auth} />
      ) : (
        <LoginPage auth={auth} />
      )}
    </ThemeProvider>
  );
}
