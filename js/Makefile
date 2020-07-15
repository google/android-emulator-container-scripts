# Copyright (C) 2019 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

MAKEFILE_PATH := $(abspath $(lastword $(MAKEFILE_LIST)))
CURRENT_DIR :=  $(abspath $(MAKEFILE_PATH)/..)

.PHONY: build-release run-release develop stop

all: develop

deps:
	@npm install

develop:
	./develop.sh

build-release:  protoc system-check
	 docker-compose -f docker/docker-compose.yaml build

run-release: build-release
	 docker-compose -f docker/docker-compose.yaml up

stop:
	docker stop emu-dev-grpc-web; pkill -9 npm; pkill -9 js; pkill -9 node; true
