import { withStyles } from "@material-ui/core/styles";

import AppBar from "@material-ui/core/AppBar";
import Box from "@material-ui/core/Box";
import Container from "@material-ui/core/Container";
import Copyright from "./copyright";
import { Emulator } from "android-emulator-webrtc/emulator";
import LogcatView from "./logcat_view";
import ExitToApp from "@material-ui/icons/ExitToApp";
import Grid from "@material-ui/core/Grid";
import IconButton from "@material-ui/core/IconButton";
import ImageIcon from "@material-ui/icons/Image";
import OndemandVideoIcon from "@material-ui/icons/OndemandVideo";
import Slider from "@material-ui/core/Slider";
import VolumeDown from "@material-ui/icons/VolumeDown";
import VolumeUp from "@material-ui/icons/VolumeUp";
import LocationOnIcon from "@material-ui/icons/LocationOn";
import PropTypes from "prop-types";
import React from "react";
import Toolbar from "@material-ui/core/Toolbar";
import Typography from "@material-ui/core/Typography";
import Snackbar from "@material-ui/core/Snackbar";
import Alert from "@material-ui/lab/Alert";

const styles = (theme) => ({
  root: {
    flexGrow: 1,
  },
  menuButton: {
    marginRight: theme.spacing(2),
  },
  title: {
    flexGrow: 1,
  },
  nofocusborder: {
    outline: "none !important;",
  },
  paper: {
    marginTop: theme.spacing(4),
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
  },
});

// We want a white slider, otherwise it will be invisible in the appbar.
const WhiteSlider = withStyles({
  thumb: {
    color: "white",
  },
  track: {
    color: "white",
  },
  rail: {
    color: "white",
  },
})(Slider);

// This class is responsible for hosting two emulator components next to each other:
// One the left it will display the emulator, and on the right it will display the
// active logcat.
//
// It uses the material-ui to display a toolbar.
class EmulatorScreen extends React.Component {
  state = {
    view: "webrtc",
    error_snack: false,
    error_msg: "",
    emuState: "connecting",
    muted: true,
    volume: 0.0,
    hasAudio: false,
    // Let's start at the Googleplex
    gps: { latitude: 37.4221, longitude: -122.0841 },
  };

  static propTypes = {
    uri: PropTypes.string, // grpc endpoint
    auth: PropTypes.object, // auth module to use.
  };

  stateChange = (s) => {
    this.setState({ emuState: s });
  };

  onAudioStateChange = (s) => {
    console.log("Received an audio state change from the emulator.");
    this.setState({ hasAudio: s });
  };

  onError = (err) => {
    this.setState({
      error_snack: true,
      error_msg: "Low level gRPC error: " + JSON.stringify(err),
    });
  };

  updateLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition((location) => {
        const loc = location.coords;
        this.setState({
          gps: { latitude: loc.latitude, longitude: loc.longitude },
        });
      });
    }
  };

  handleClose = (e) => {
    this.setState({ error_snack: false });
  };

  handleVolumeChange = (e, newVolume) => {
    const muted = newVolume === 0;
    this.setState({ volume: newVolume, muted: muted });
  };

  render() {
    const { uri, auth, classes } = this.props;
    const {
      view,
      emuState,
      error_snack,
      error_msg,
      muted,
      volume,
      hasAudio,
      gps,
    } = this.state;
    return (
      <div className={classes.root}>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" className={classes.title}>
              Using emulator view: {view}
            </Typography>

            {hasAudio ? ( // Only display volume control if this emulator supports audio.
              <Box width={200} paddingTop={1}>
                <Grid container spacing={2}>
                  <Grid item>
                    <VolumeDown />
                  </Grid>
                  <Grid item xs>
                    <WhiteSlider
                      value={volume}
                      onChange={this.handleVolumeChange}
                      min={0.0}
                      max={1.0}
                      step={0.01}
                      aria-labelledby="continuous-slider"
                    />
                  </Grid>
                  <Grid item>
                    <VolumeUp />
                  </Grid>
                </Grid>
              </Box>
            ) : (
              // No audio track, so no volume slider.
              <div />
            )}

            <div className={classes.grow} />
            <div className={classes.sectionDesktop}>
              <IconButton
                aria-label="Get current location"
                color="inherit"
                onClick={this.updateLocation}
              >
                <LocationOnIcon />
              </IconButton>
              <IconButton
                aria-label="Switch to webrtc"
                color="inherit"
                onClick={() => this.setState({ view: "webrtc" })}
              >
                <OndemandVideoIcon />
              </IconButton>
              <IconButton
                aria-label="Switch to screenshots"
                color="inherit"
                onClick={() => this.setState({ view: "png" })}
              >
                <ImageIcon />
              </IconButton>
              <IconButton
                edge="end"
                aria-label="logout"
                color="inherit"
                onClick={() => auth.logout()}
              >
                <ExitToApp />
              </IconButton>
            </div>
          </Toolbar>
        </AppBar>

        <div className={classes.paper}>
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6}>
              <Container maxWidth="sm">
                <Emulator
                  uri={uri}
                  auth={auth}
                  view={this.state.view}
                  onStateChange={this.stateChange}
                  onAudioStateChange={this.onAudioStateChange}
                  onError={this.onError}
                  muted={muted}
                  volume={volume}
                  gps={gps}
                />
                <p>State: {emuState} </p>
              </Container>
            </Grid>
            <Grid item xs={12} sm={6}>
              <LogcatView uri={uri} auth={auth} />
            </Grid>
          </Grid>
        </div>
        <Box mt={8}>
          <Copyright />
        </Box>
        <Snackbar open={error_snack} autoHideDuration={6000}>
          <Alert onClose={this.handleClose} severity="error">
            {error_msg}
          </Alert>
        </Snackbar>
      </div>
    );
  }
}

export default withStyles(styles)(EmulatorScreen);
