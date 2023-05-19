import { withStyles } from "@material-ui/core/styles";

import Avatar from "@material-ui/core/Avatar";
import Box from "@material-ui/core/Box";
import Button from "@material-ui/core/Button";
import Container from "@material-ui/core/Container";
import Copyright from "./copyright";
import CssBaseline from "@material-ui/core/CssBaseline";
import LockOutlinedIcon from "@material-ui/icons/LockOutlined";
import PropTypes from "prop-types";
import React from "react";
import Typography from "@material-ui/core/Typography";
import * as firebase from "firebase/app";
import "firebase/auth";
import {
    FirebaseAuthProvider,
    FirebaseAuthConsumer
} from "@react-firebase/auth";
import { config } from "../config";

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

// A basic login page using firebase.
class SignIn extends React.Component {
    state = {
        email: "",
        password: "",
    };

    static propTypes = {
        auth: PropTypes.object.isRequired // Auth service
    };

    loginGoogle = () => {
        const googleAuthProvider = new firebase.auth.GoogleAuthProvider();
        firebase.auth().signInWithPopup(googleAuthProvider);
    }

    render() {
        const { classes, auth } = this.props;

        return (
            <FirebaseAuthProvider {...config} firebase={firebase}>
                <Container component="main" maxWidth="xs">
                    <CssBaseline />
                    <div className={classes.paper}>
                        <Avatar className={classes.avatar}>
                            <LockOutlinedIcon />
                        </Avatar>
                        <Typography component="h1" variant="h5">Sign in</Typography>
                        <Box mt={8}>
                            <Button variant="contained" color="primary" onClick={this.loginGoogle} >Sign in with Google</Button>
                        </Box>
                    </div>
                    <Box mt={8}>
                        <Copyright />
                    </Box>
                </Container>
                <FirebaseAuthConsumer>
                    {({ isSignedIn, user, providerId }) => {
                        console.log(`Firebase login: isSignedId: ${isSignedIn}`)
                        if (isSignedIn) {
                            firebase.auth().currentUser.getIdToken().then(function (token) {
                                auth.setToken(`Bearer ${token}`);
                            });

                        }
                    }}
                </FirebaseAuthConsumer>
            </FirebaseAuthProvider>

        );
    }
}

export default withStyles(useStyles)(SignIn);
