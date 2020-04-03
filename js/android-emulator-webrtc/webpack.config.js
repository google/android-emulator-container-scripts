var path = require("path");

module.exports = {
  mode: "production",
  entry: "./src/index.js",
  output: {
    path: path.resolve("emulator"),
    filename: "index.js",
    library: "android-emulator-webrtc",
    libraryTarget: "umd"
  },
  optimization: {
    // Set this to false during debuging time..
    minimize: false,
    usedExports: true
  },
  module: {
    rules: [
      {
        test: /\.jsx?$/,
        exclude: [
          /(node_modules)/
        ],
        use: "babel-loader"
      }
    ]
  }
}
