#!/bin/sh
trap killgroup SIGINT

killgroup(){
  echo killing... be patient...
  docker stop emu-dev-grpc-web
  kill 0
}

cd "$(dirname "$0")"
BUILD_OS=$(uname -s)
case $BUILD_OS in
  Darwin)
    echo "Building for Mac"
    docker build -t emu-dev-web -f develop/Dockerfile.mac develop
    ;;
  *)
    echo "Building for linux"
    docker build -t emu-dev-web -f develop/Dockerfile.unix develop
    ;;
esac
docker rm emu-dev-grpc-web
docker run  -p 8080:8080 -p 8001:8001  --name emu-dev-grpc-web emu-dev-web &
npm start &
wait
