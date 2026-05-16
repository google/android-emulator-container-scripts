import React, { useEffect } from "react";
import { initializeApp } from "firebase/app";
import {
    getAuth,
    GoogleAuthProvider,
    signInWithPopup,
    onAuthStateChanged,
} from "firebase/auth";

import PropTypes from "prop-types";
import withStyles from "@mui/styles/withStyles";

import Avatar from "@mui/material/Avatar";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Container from "@mui/material/Container";
import Copyright from "./copyright";
import CssBaseline from "@mui/material/CssBaseline";
import LockOutlinedIcon from "@mui/icons-material/LockOutlined";
import Typography from "@mui/material/Typography";

import { config } from "../config";

// Initialize the Firebase app once at module load.
const firebaseApp = initializeApp(config);
const firebaseAuth = getAuth(firebaseApp);

const useStyles = theme => ({
    "@global": {
        body: {
            backgroundColor: theme.palette.common.white,
        },
    },
    paper: {
        marginTop: theme.spacing(8),
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
    },
    avatar: {
        margin: theme.spacing(1),
        backgroundColor: theme.palette.secondary.main,
    },
    form: {
        width: "100%",
        marginTop: theme.spacing(1),
    },
    submit: {
        margin: theme.spacing(3, 0, 2),
    },
});

// A basic login page using Firebase Auth (modular SDK).
function SignIn({ classes, auth }) {
    useEffect(() => {
        // Subscribe to Firebase auth-state changes; on every transition to
        // signed-in, push a fresh ID token into the local auth service so
        // gRPC requests get the right Bearer header.
        return onAuthStateChanged(firebaseAuth, async user => {
            if (user) {
                const token = await user.getIdToken();
                auth.setToken(`Bearer ${token}`);
            }
        });
    }, [auth]);

    const handleSignIn = () => {
        signInWithPopup(firebaseAuth, new GoogleAuthProvider()).catch(err =>
            console.error("Firebase sign-in failed:", err)
        );
    };

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
                <Box mt={8}>
                    <Button
                        variant="contained"
                        color="primary"
                        onClick={handleSignIn}
                    >
                        Sign in with Google
                    </Button>
                </Box>
            </div>
            <Box mt={8}>
                <Copyright />
            </Box>
        </Container>
    );
}

SignIn.propTypes = {
    auth: PropTypes.object.isRequired, // Local auth service
};

export default withStyles(useStyles)(SignIn);
