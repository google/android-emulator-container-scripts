import { withStyles } from "@material-ui/core/styles";

import Avatar from "@material-ui/core/Avatar";
import Box from "@material-ui/core/Box";
import Button from "@material-ui/core/Button";
import CloseIcon from "@material-ui/icons/Close";
import Container from "@material-ui/core/Container";
import Copyright from "./copyright";
import CssBaseline from "@material-ui/core/CssBaseline";
import IconButton from "@material-ui/core/IconButton";
import LockOutlinedIcon from "@material-ui/icons/LockOutlined";
import PropTypes from "prop-types";
import React from "react";
import Snackbar from "@material-ui/core/Snackbar";
import TextField from "@material-ui/core/TextField";
import Typography from "@material-ui/core/Typography";

const useStyles = theme => ({
  "@global": {
    body: {
      backgroundColor: theme.palette.common.white
    }
  },
  paper: {
    marginTop: theme.spacing(8),
    display: "flex",
    flexDirection: "column",
    alignItems: "center"
  },
  avatar: {
    margin: theme.spacing(1),
    backgroundColor: theme.palette.secondary.main
  },
  form: {
    width: "100%", // Fix IE 11 issue.
    marginTop: theme.spacing(1)
  },
  submit: {
    margin: theme.spacing(3, 0, 2)
  }
});

// A simple material-ui signin page that will call the auth service to
// perform a login.
class SignIn extends React.Component {
  state = {
    email: "",
    password: "",
    displayErrorSnack: false
  };

  static propTypes = {
    auth: PropTypes.object.isRequired // Auth service
  };

  updateEmail = event => {
    this.setState({ email: event.target.value });
  };

  updatePassword = event => {
    this.setState({ password: event.target.value });
  };

  doLogin = () => {
    const { auth } = this.props;
    const { email, password } = this.state;
    auth.login(email, password).catch(e => {
      this.setState({ displayErrorSnack: true });
    });
  };

  // Login when we press the enter key
  handleTextFieldKeyDown = event => {
    if (event.key === "Enter") this.doLogin();
  };

  render() {
    const { classes } = this.props;
    const { displayErrorSnack } = this.state;
    return (
      <Container component="main" maxWidth="xs">
        <CssBaseline />
        <div className={classes.paper}>
          <Avatar className={classes.avatar}>
            <LockOutlinedIcon />
          </Avatar>
          <Typography component="h1" variant="h5">
            Sign in
          </Typography>

          <Snackbar
            open={displayErrorSnack}
            autoHideDuration={4000}
            ContentProps={{
              "aria-describedby": "snackbar-fab-message-id"
            }}
            message={
              <span id="snackbar-fab-message-id">Failed to login..</span>
            }
            //className={classes.snackbar}
            onClose={() => {
              this.setState({ displayErrorSnack: false });
            }}
            action={[
              <IconButton
                key="close"
                aria-label="close"
                color="inherit"
                onClick={() => {
                  this.setState({ displayErrorSnack: false });
                }}
              >
                <CloseIcon className={classes.icon} />
              </IconButton>
            ]}
          />
          <form className={classes.form} noValidate>
            <TextField
              variant="outlined"
              margin="normal"
              required
              fullWidth
              id="email"
              label="Email Address"
              name="email"
              autoComplete="email"
              autoFocus
              value={this.state.email}
              onChange={this.updateEmail}
            />
            <TextField
              variant="outlined"
              margin="normal"
              required
              fullWidth
              name="password"
              label="Password"
              type="password"
              id="password"
              autoComplete="current-password"
              value={this.state.password}
              onChange={this.updatePassword}
              onKeyDown={this.handleTextFieldKeyDown}
            />
            <Button
              fullWidth
              variant="contained"
              color="primary"
              className={classes.submit}
              onClick={this.doLogin}
            >
              Sign In
            </Button>
          </form>
        </div>
        <Box mt={8}>
          <Copyright />
        </Box>
      </Container>
    );
  }
}

export default withStyles(useStyles)(SignIn);
