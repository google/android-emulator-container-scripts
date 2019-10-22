import { withStyles } from "@material-ui/core/styles";

import AppBar from "@material-ui/core/AppBar";
import Box from "@material-ui/core/Box";
import Container from "@material-ui/core/Container";
import Copyright from "./copyright";
import Emulator from "./emulator/emulator.js";
import ExitToApp from "@material-ui/icons/ExitToApp";
import Grid from "@material-ui/core/Grid";
import IconButton from "@material-ui/core/IconButton";
import ImageIcon from "@material-ui/icons/Image";
import LogcatView from "./emulator/views/logcat_view";
import OndemandVideoIcon from "@material-ui/icons/OndemandVideo";
import PropTypes from "prop-types";
import React from "react";
import Toolbar from "@material-ui/core/Toolbar";
import Typography from "@material-ui/core/Typography";

const styles = theme => ({
  root: {
    flexGrow: 1
  },
  menuButton: {
    marginRight: theme.spacing(2)
  },
  title: {
    flexGrow: 1
  },
  nofocusborder: {
    outline: "none !important;"
  },
  paper: {
    marginTop: theme.spacing(4),
    display: "flex",
    flexDirection: "column",
    alignItems: "center"
  }
});

// This class is responsible for hosting two emulator components next to each other:
// One the left it will display the emulator, and on the right it will display the
// active logcat.
//
// It uses the material-ui to display a toolbar.
class EmulatorScreen extends React.Component {
  state = {
    view: "webrtc"
  };

  static propTypes = {
    emulator: PropTypes.object, // emulator service
    auth: PropTypes.object
  };

  render() {
    const { emulator, auth, classes } = this.props;
    const { view } = this.state;
    return (
      <div className={classes.root}>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" className={classes.title}>
              Using emulator view: {view}
            </Typography>
            <div className={classes.grow} />
            <div className={classes.sectionDesktop}>
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
                <Emulator emulator={emulator} view={this.state.view} />
              </Container>
            </Grid>

            <Grid item xs={12} sm={6}>
              <LogcatView emulator={emulator} maxHistory={8} />
            </Grid>
          </Grid>
        </div>

        <Box mt={8}>
          <Copyright />
        </Box>
      </div>
    );
  }
}

export default withStyles(styles)(EmulatorScreen);
