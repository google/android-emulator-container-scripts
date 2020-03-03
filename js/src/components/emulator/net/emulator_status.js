/*
 * Copyright 2020 The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License")
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
import { Empty } from "google-protobuf/google/protobuf/empty_pb";

/**
 * Gets the status of the emulator, parsing the hardware config into something
 * easy to digest.
 *
 * @export
 * @class EmulatorStatus
 */
export default class EmulatorStatus {
  constructor(emulator) {
    this.emulator = emulator;
    this.status = null;
  }

  getStatus = () => {
    return this.status;
  };

  /**
   * Update the status of the emulator
   *
   * @param  {Callback} fnNotify when the status is available, returns the retrieved status.
   * @memberof EmulatorStatus
   */
  updateStatus = fnNotify => {
    const request = new Empty();
    this.emulator.getStatus(request).on("data", response => {
      var hwConfig = {};
      const entryList = response.getHardwareconfig().getEntryList();
      for (var i = 0; i < entryList.length; i++) {
        const key = entryList[i].getKey();
        const val = entryList[i].getValue();
        hwConfig[key] = val;
      }

      const vmConfig = response.getVmconfig();
      this.status = {
        version: response.getVersion(),
        uptime: response.getUptime(),
        booted: response.getBooted(),
        hardwareConfig: hwConfig,
        vmConfig: {
          hypervisorType: vmConfig.getHypervisortype(),
          numberOfCpuCores: vmConfig.getNumberofcpucores(),
          ramSizeBytes: vmConfig.getRamsizebytes()
        }
      };
      fnNotify(this.status);
    });
  };
}
