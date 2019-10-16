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
GOCMD=go
GOPATH = $(shell $(GOCMD) env GOPATH)

DEP=dep
PROTOC=protoc
PROTOC_CMD = which $(PROTOC)

# Check that the minimum protocol version >3.6
MIN_PROTOC_VERSION=3.6
PROTOC_VERSION=($(PROTOC_CMD) --version |  sed 's/[[:alpha:]|(|[:space:]]//g'; echo $(MIN_PROTOC_VERSION)) | sort -V | head -n 1
PROTOHEADER=$(shell pkg-config --variable prefix protobuf)/include
PROTOLIB=$(shell pkg-config --variable prefix protobuf)/lib

HAS_PROTOC = $(shell $(PROTOC_CMD) > /dev/null && echo true || echo false)
HAS_DEP = $(shell which $(DEP) > /dev/null && echo true || echo false)

ifeq ($(HAS_PROTOC),true)
	HAS_VALID_PROTOC := $(subst $(MIN_PROTOC_VERSION),true,$(shell $(PROTOC_VERSION)))
endif

ifeq ($(HAS_VALID_PROTOC),true)
	ifneq (,$(wildcard $(PROTOHEADER)/google/protobuf/compiler/code_generator.h))
		HAS_VALID_PROTOC := true
	else
		HAS_VALID_PROTOC := false
	endif
endif


SYSTEM_OK = false
ifeq ($(HAS_VALID_PROTOC),true)
  	SYSTEM_OK = true
endif


MAKEFILE_PATH := $(abspath $(lastword $(MAKEFILE_LIST)))
QEMU_ROOT := $(abspath $(MAKEFILE_PATH)/../../../../../..)
CURRENT_DIR :=  $(abspath $(MAKEFILE_PATH)/..)
OUT_DIR := $(CURRENT_DIR)/src/
CONTROLPB = $(OUT_DIR)/android_emulation_control/emulator_controller_pb.js
GRPCPB = $(OUT_DIR)/android_emulation_control/emulator_controller_grpc_web_pb.js
PROTODIR = $(CURRENT_DIR)/android_emulation_control
PROTO = $(PROTODIR)/emulator_controller.proto

CXX = g++
CPPFLAGS += -I$(PROTOHEADER) -pthread
CXXFLAGS += -std=c++11
LDFLAGS += -L$(PROTOLIB) -lprotoc -lprotobuf -lpthread -ldl

.PHONY: build-release run-release develop stop

all: develop

clean:
	rm $(PROTO) $(CONTROLPB) $(GRPCPB)

$(PROTO):
		mkdir -p $(PROTODIR)
ifeq (,$(wildcard $(QEMU_ROOT)/android/android-grpc/android/emulation/control/emulator_controller.proto))
		cp  $(ANDROID_SDK_ROOT)/emulator/lib/emulator_controller.proto  $(PROTO)
else
		cp  $(QEMU_ROOT)/android/android-grpc/android/emulation/control/emulator_controller.proto  $(PROTO)
endif

protoc-gen-grpc-web: protoc-plugin/grpc_generator.o
	$(CXX) $^ $(LDFLAGS) -o $@

$(CONTROLPB) $(GRPCPB): $(PROTO) protoc-gen-grpc-web
	@mkdir -p $(OUT_DIR)/android_emulation_control
	$(PROTOC)  -I/usr/local/include -I$(PROTODIR) \
			--plugin=protoc-gen-grpc-web=$(CURRENT_DIR)/protoc-gen-grpc-web \
			--js_out=import_style=commonjs:/tmp \
			--grpc-web_out=import_style=commonjs,mode=grpcwebtext:/tmp \
			$(PROTO)
	@echo "/* eslint-disable */" > $(CONTROLPB)
	@cat /tmp/emulator_controller_pb.js >>  $(CONTROLPB)
	@cp  /tmp/emulator_controller_grpc_web_pb.js $(GRPCPB)


deps: $(CONTROLPB) $(GRPCPB) system-check
	@npm install

develop: $(CONTROLPB) $(GRPCPB)
	./develop.sh

build-release:  $(CONTROLPB) $(GRPCPB) system-check
	 docker-compose -f docker/docker-compose.yaml build

run-release: build-release
	 docker-compose -f docker/docker-compose.yaml up

stop:
	docker stop emu-dev-grpc-web; pkill -9 npm; pkill -9 js; pkill -9 node; true



system-check:
ifneq ($(HAS_VALID_PROTOC),true)
	@echo " DEPENDENCY ERROR"
	@echo
	@echo "You don't have protoc 3.6.0 installed in your path."
	@echo "Please install Google protocol buffers 3.6.0 and its compiler."
	@echo "You can find it here:"
	@echo
	@echo "   https://github.com/google/protobuf/releases/tag/v3.6.0"
	@echo "   or try $ brew install protoc"
	@echo
	@echo "Here is what I get when trying to evaluate your version of protoc:"
	@echo
	-$(PROTOC) --version
	@echo
	@echo "And here is where I am looking for the headers: $(PROTOHEADER)/google/protobuf"
	@echo
endif
ifneq ($(SYSTEM_OK),true)
	@false
endif
