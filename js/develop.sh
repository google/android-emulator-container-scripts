#!/bin/sh
trap killgroup SIGINT

killgroup(){
   echo killing... be patient...
   docker stop emu-dev-grpc-web
   kill 0
}

docker build -t emu-dev-web -f develop/envoy.Dockerfile develop

cd "$(dirname "$0")"
BUILD_OS=$(uname -s)
case $BUILD_OS in
   Darwin)
      echo "Building for Mac"
      docker run --rm -p 8080:8080 -p 8001:8001 --name emu-dev-grpc-web emu-dev-web &
      ;;
   *)
      echo "Building for linux"
      docker run --rm -p 8080:8080 -p 8001:8001 --name emu-dev-grpc-web "--add-host=host.docker.internal:host-gateway" emu-dev-web &
      ;;
esac

echo "Make sure you are running the android emulator & video bridge"
echo "Launch the video bridge with 'goldfish-webrtc-bridge --port 9554'"

npm start
