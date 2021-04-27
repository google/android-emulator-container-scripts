# Copyright 2019 - The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
FROM debian:stretch-slim
ARG apt_repo_mirror
RUN if [ x"$apt_repo_mirror" != "x" ]; then \
    sed -i -E "s#http(s)?://[^\/]+#${apt_repo_mirror}#g" /etc/apt/sources.list;  \
    fi
RUN apt-get update -y && \
    apt-get install -y python-pip python-dev build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
COPY . /app
WORKDIR /app
ARG pip_index
RUN if [ x"$pip_index" = "x" ]; then \
    pip install -r requirements.txt; \
    else \
    pip install -i ${pip_index} -r requirements.txt; \
    fi
ENTRYPOINT ["python"]
CMD ["jwt-provider.py"]
