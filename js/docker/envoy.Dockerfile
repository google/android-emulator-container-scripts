# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#FROM envoyproxy/envoy:latest
FROM envoyproxy/envoy:latest

COPY ./envoy.yaml /etc/envoy/envoy.yaml
ADD certs/self_sign.crt /etc/cert.crt
ADD certs/self_sign.key /etc/key.key
ADD certs/jwt_secrets_pub.jwks /etc/jwt_secrets_pub.jwks
CMD /usr/local/bin/envoy -c /etc/envoy/envoy.yaml
