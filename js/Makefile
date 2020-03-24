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
PROTOC=protoc
PROTOC_CMD = which $(PROTOC)

# Check that the minimum protocol version >3.6
PROTOHEADER=$(shell pkg-config --variable prefix protobuf)/include
PROTOLIB=$(shell pkg-config --variable prefix protobuf)/lib

HAS_PROTOC = $(shell $(PROTOC_CMD) > /dev/null && echo true || echo false)
HAS_DEP = $(shell which $(DEP) > /dev/null && echo true || echo false)

# Prefixing works differently on mac vs linux, so let us account for that.

UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
	PREFIX_ESLINT = sed -i -e '1i\'$$'\n''/* eslint-disable */'$$'\n'''
endif
ifeq ($(UNAME_S),Darwin)
	PREFIX_ESLINT = sed -i '' -e '1i\'$$'\n''/* eslint-disable */'$$'\n'''
endif

ifeq ($(HAS_PROTOC),true)
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
CURRENT_DIR :=  $(abspath $(MAKEFILE_PATH)/..)
QEMU_ROOT := $(abspath $(AOSP)/external/qemu)
DOCKER_SRC_ROOT := $(abspath $(CURRENT_DIR)/../src/emu)
GRPC_ROOT := $(QEMU_ROOT)/objs/distribution/emulator/lib

# Protobuf settings. If you are running this in the AOSP tree you will want to run ninja install first.
PROTODIR 	  := $(CURRENT_DIR)/src/android_emulation_control/
PROTOSRCDIR   := $(if $(wildcard $(GRPC_ROOT)/*.proto), $(GRPC_ROOT), $(DOCKER_SRC_ROOT)/emulator/lib)
PROTO_SRC     := $(wildcard $(PROTOSRCDIR)/*.proto)
PROTO_OBJS    := $(addprefix $(PROTODIR)/, $(notdir $(PROTO_SRC:.proto=_pb.js)))
PROXY_OBJS    := $(addprefix $(PROTODIR)/, $(notdir $(PROTO_SRC:.proto=_grpc_web_pb.js)))


CXX = g++
CPPFLAGS += -I$(PROTOHEADER) -pthread
CXXFLAGS += -std=c++11
LDFLAGS += -L$(PROTOLIB) -lprotoc -lprotobuf -lpthread -ldl

.PHONY: build-release run-release develop stop

all: develop

clean:
	rm -rf $(PROTODIR)


$(PROTODIR):
	@mkdir -p $(PROTODIR)

# Protobuf --> js (note technically this produces 2 files.) which is not
# the way you are supposed to do things in gnumake
# https://www.gnu.org/software/automake/manual/html_node/Multiple-Outputs.html
# Use sed to insert the /* eslint-disable */ at the start of the file
# \`$$`\n` forces a real newline char, because make.
$(PROTODIR)/%_pb.js  : $(PROTOSRCDIR)/%.proto $(PROTODIR) protoc-gen-grpc-web
	$(PROTOC) \
	        -I/usr/local/include -I$(PROTODIR) -I$(PROTOSRCDIR) \
			--plugin=protoc-gen-grpc-web=$(CURRENT_DIR)/protoc-gen-grpc-web \
			--js_out=import_style=commonjs:$(PROTODIR) \
			--grpc-web_out=import_style=commonjs,mode=grpcwebtext:$(PROTODIR) \
			$<
	$(PREFIX_ESLINT) $@

# Fix up the proxies _grpc_web files by prefixing  /* eslint-disable */
# Not evey source produces a _grpc_web, so we onle do the replace if them file exists, otherwise it is a nop.
$(PROTODIR)/%_grpc_web_pb.js : $(PROTODIR)/%_pb.js
	@test -f $@  && $(PREFIX_ESLINT) $@ || true

$(PROTODIR)/emulator_web_client.js:
	if [ -f "$(PROTODIR)/rtc_service_pb.js" ]; then  \
		cp src/ext/emulator_web_client_v2.js $(PROTODIR)/emulator_web_client.js; \
	else  \
		cp src/ext/emulator_web_client_v1.js $(PROTODIR)/emulator_web_client.js; \
	fi


protoc: $(PROTO_OBJS) $(PROXY_OBJS) $(PROTODIR)/emulator_web_client.js

protoc-gen-grpc-web: protoc-plugin/grpc_generator.o
	$(CXX) $^ $(LDFLAGS) -o $@

deps: protoc system-check

	@npm install

develop: protoc
	./develop.sh

build-release:  protoc system-check
	 docker-compose -f docker/docker-compose.yaml build

run-release: build-release
	 docker-compose -f docker/docker-compose.yaml up

stop:
	docker stop emu-dev-grpc-web; pkill -9 npm; pkill -9 js; pkill -9 node; true


system-check:
ifneq ($(HAS_VALID_PROTOC),true)
	@echo " DEPENDENCY ERROR"
	@echo
	@echo "You don't have protoc 3.6.0 > installed in your path."
	@echo "Please install Google protocol buffers 3.6.0> and its compiler."
	@echo "You can find it here:"
	@echo
	@echo "   https://github.com/google/protobuf/releases/tag/v3.6.0"
	@echo "   or try $ brew install protobuf"
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
