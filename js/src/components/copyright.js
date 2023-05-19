/**
 * @fileoverview Description of this file.
 */
import React, { Component } from "react";
import Typography from "@mui/material/Typography";
import Link from "@mui/material/Link";

export default class Copyright extends Component {
  render() {
    return (
      <Typography variant="body2" color="textSecondary" align="center">
        {"Copyright © "}
        <Link color="inherit" href="https://material-ui.com/">
          Your Website
        </Link>{" "}
        {new Date().getFullYear()}
        {"."}
      </Typography>
    );
  }
}
