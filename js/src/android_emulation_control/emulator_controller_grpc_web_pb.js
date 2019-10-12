/**
 * @fileoverview gRPC-Web generated client stub for android.emulation.control
 * @enhanceable
 * @public
 */

// GENERATED CODE -- DO NOT EDIT!



const grpc = {};
grpc.web = require('grpc-web');


var google_protobuf_empty_pb = require('google-protobuf/google/protobuf/empty_pb.js')
const proto = {};
proto.android = {};
proto.android.emulation = {};
proto.android.emulation.control = require('./emulator_controller_pb.js');

/**
 * @param {string} hostname
 * @param {?Object} credentials
 * @param {?Object} options
 * @constructor
 * @struct
 * @final
 */
proto.android.emulation.control.EmulatorControllerClient =
    function(hostname, credentials, options) {
  if (!options) options = {};
  options['format'] = 'text';

  /**
   * @private @const {!grpc.web.GrpcWebClientBase} The client
   */
  this.client_ = new grpc.web.GrpcWebClientBase(options);

  /**
   * @private @const {string} The hostname
   */
  this.hostname_ = hostname;

  /**
   * @private @const {?Object} The credentials to be used to connect
   *    to the server
   */
  this.credentials_ = credentials;

  /**
   * @private @const {?Object} Options for the client
   */
  this.options_ = options;
};


/**
 * @param {string} hostname
 * @param {?Object} credentials
 * @param {?Object} options
 * @constructor
 * @struct
 * @final
 */
proto.android.emulation.control.EmulatorControllerPromiseClient =
    function(hostname, credentials, options) {
  if (!options) options = {};
  options['format'] = 'text';

  /**
   * @private @const {!grpc.web.GrpcWebClientBase} The client
   */
  this.client_ = new grpc.web.GrpcWebClientBase(options);

  /**
   * @private @const {string} The hostname
   */
  this.hostname_ = hostname;

  /**
   * @private @const {?Object} The credentials to be used to connect
   *    to the server
   */
  this.credentials_ = credentials;

  /**
   * @private @const {?Object} Options for the client
   */
  this.options_ = options;
};


/**
 * @const
 * @type {!grpc.web.AbstractClientBase.MethodInfo<
 *   !proto.android.emulation.control.Rotation,
 *   !proto.android.emulation.control.Rotation>}
 */
const methodInfo_EmulatorController_setRotation = new grpc.web.AbstractClientBase.MethodInfo(
  proto.android.emulation.control.Rotation,
  /** @param {!proto.android.emulation.control.Rotation} request */
  function(request) {
    return request.serializeBinary();
  },
  proto.android.emulation.control.Rotation.deserializeBinary
);


/**
 * @param {!proto.android.emulation.control.Rotation} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @param {function(?grpc.web.Error, ?proto.android.emulation.control.Rotation)}
 *     callback The callback function(error, response)
 * @return {!grpc.web.ClientReadableStream<!proto.android.emulation.control.Rotation>|undefined}
 *     The XHR Node Readable Stream
 */
proto.android.emulation.control.EmulatorControllerClient.prototype.setRotation =
    function(request, metadata, callback) {
  return this.client_.rpcCall(this.hostname_ +
      '/android.emulation.control.EmulatorController/setRotation',
      request,
      metadata || {},
      methodInfo_EmulatorController_setRotation,
      callback);
};


/**
 * @param {!proto.android.emulation.control.Rotation} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @return {!Promise<!proto.android.emulation.control.Rotation>}
 *     A native promise that resolves to the response
 */
proto.android.emulation.control.EmulatorControllerPromiseClient.prototype.setRotation =
    function(request, metadata) {
  return this.client_.unaryCall(this.hostname_ +
      '/android.emulation.control.EmulatorController/setRotation',
      request,
      metadata || {},
      methodInfo_EmulatorController_setRotation);
};


/**
 * @const
 * @type {!grpc.web.AbstractClientBase.MethodInfo<
 *   !proto.google.protobuf.Empty,
 *   !proto.android.emulation.control.Rotation>}
 */
const methodInfo_EmulatorController_getRotation = new grpc.web.AbstractClientBase.MethodInfo(
  proto.android.emulation.control.Rotation,
  /** @param {!proto.google.protobuf.Empty} request */
  function(request) {
    return request.serializeBinary();
  },
  proto.android.emulation.control.Rotation.deserializeBinary
);


/**
 * @param {!proto.google.protobuf.Empty} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @param {function(?grpc.web.Error, ?proto.android.emulation.control.Rotation)}
 *     callback The callback function(error, response)
 * @return {!grpc.web.ClientReadableStream<!proto.android.emulation.control.Rotation>|undefined}
 *     The XHR Node Readable Stream
 */
proto.android.emulation.control.EmulatorControllerClient.prototype.getRotation =
    function(request, metadata, callback) {
  return this.client_.rpcCall(this.hostname_ +
      '/android.emulation.control.EmulatorController/getRotation',
      request,
      metadata || {},
      methodInfo_EmulatorController_getRotation,
      callback);
};


/**
 * @param {!proto.google.protobuf.Empty} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @return {!Promise<!proto.android.emulation.control.Rotation>}
 *     A native promise that resolves to the response
 */
proto.android.emulation.control.EmulatorControllerPromiseClient.prototype.getRotation =
    function(request, metadata) {
  return this.client_.unaryCall(this.hostname_ +
      '/android.emulation.control.EmulatorController/getRotation',
      request,
      metadata || {},
      methodInfo_EmulatorController_getRotation);
};


/**
 * @const
 * @type {!grpc.web.AbstractClientBase.MethodInfo<
 *   !proto.android.emulation.control.BatteryState,
 *   !proto.android.emulation.control.BatteryState>}
 */
const methodInfo_EmulatorController_setBattery = new grpc.web.AbstractClientBase.MethodInfo(
  proto.android.emulation.control.BatteryState,
  /** @param {!proto.android.emulation.control.BatteryState} request */
  function(request) {
    return request.serializeBinary();
  },
  proto.android.emulation.control.BatteryState.deserializeBinary
);


/**
 * @param {!proto.android.emulation.control.BatteryState} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @param {function(?grpc.web.Error, ?proto.android.emulation.control.BatteryState)}
 *     callback The callback function(error, response)
 * @return {!grpc.web.ClientReadableStream<!proto.android.emulation.control.BatteryState>|undefined}
 *     The XHR Node Readable Stream
 */
proto.android.emulation.control.EmulatorControllerClient.prototype.setBattery =
    function(request, metadata, callback) {
  return this.client_.rpcCall(this.hostname_ +
      '/android.emulation.control.EmulatorController/setBattery',
      request,
      metadata || {},
      methodInfo_EmulatorController_setBattery,
      callback);
};


/**
 * @param {!proto.android.emulation.control.BatteryState} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @return {!Promise<!proto.android.emulation.control.BatteryState>}
 *     A native promise that resolves to the response
 */
proto.android.emulation.control.EmulatorControllerPromiseClient.prototype.setBattery =
    function(request, metadata) {
  return this.client_.unaryCall(this.hostname_ +
      '/android.emulation.control.EmulatorController/setBattery',
      request,
      metadata || {},
      methodInfo_EmulatorController_setBattery);
};


/**
 * @const
 * @type {!grpc.web.AbstractClientBase.MethodInfo<
 *   !proto.google.protobuf.Empty,
 *   !proto.android.emulation.control.BatteryState>}
 */
const methodInfo_EmulatorController_getBattery = new grpc.web.AbstractClientBase.MethodInfo(
  proto.android.emulation.control.BatteryState,
  /** @param {!proto.google.protobuf.Empty} request */
  function(request) {
    return request.serializeBinary();
  },
  proto.android.emulation.control.BatteryState.deserializeBinary
);


/**
 * @param {!proto.google.protobuf.Empty} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @param {function(?grpc.web.Error, ?proto.android.emulation.control.BatteryState)}
 *     callback The callback function(error, response)
 * @return {!grpc.web.ClientReadableStream<!proto.android.emulation.control.BatteryState>|undefined}
 *     The XHR Node Readable Stream
 */
proto.android.emulation.control.EmulatorControllerClient.prototype.getBattery =
    function(request, metadata, callback) {
  return this.client_.rpcCall(this.hostname_ +
      '/android.emulation.control.EmulatorController/getBattery',
      request,
      metadata || {},
      methodInfo_EmulatorController_getBattery,
      callback);
};


/**
 * @param {!proto.google.protobuf.Empty} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @return {!Promise<!proto.android.emulation.control.BatteryState>}
 *     A native promise that resolves to the response
 */
proto.android.emulation.control.EmulatorControllerPromiseClient.prototype.getBattery =
    function(request, metadata) {
  return this.client_.unaryCall(this.hostname_ +
      '/android.emulation.control.EmulatorController/getBattery',
      request,
      metadata || {},
      methodInfo_EmulatorController_getBattery);
};


/**
 * @const
 * @type {!grpc.web.AbstractClientBase.MethodInfo<
 *   !proto.google.protobuf.Empty,
 *   !proto.android.emulation.control.GpsState>}
 */
const methodInfo_EmulatorController_getGps = new grpc.web.AbstractClientBase.MethodInfo(
  proto.android.emulation.control.GpsState,
  /** @param {!proto.google.protobuf.Empty} request */
  function(request) {
    return request.serializeBinary();
  },
  proto.android.emulation.control.GpsState.deserializeBinary
);


/**
 * @param {!proto.google.protobuf.Empty} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @param {function(?grpc.web.Error, ?proto.android.emulation.control.GpsState)}
 *     callback The callback function(error, response)
 * @return {!grpc.web.ClientReadableStream<!proto.android.emulation.control.GpsState>|undefined}
 *     The XHR Node Readable Stream
 */
proto.android.emulation.control.EmulatorControllerClient.prototype.getGps =
    function(request, metadata, callback) {
  return this.client_.rpcCall(this.hostname_ +
      '/android.emulation.control.EmulatorController/getGps',
      request,
      metadata || {},
      methodInfo_EmulatorController_getGps,
      callback);
};


/**
 * @param {!proto.google.protobuf.Empty} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @return {!Promise<!proto.android.emulation.control.GpsState>}
 *     A native promise that resolves to the response
 */
proto.android.emulation.control.EmulatorControllerPromiseClient.prototype.getGps =
    function(request, metadata) {
  return this.client_.unaryCall(this.hostname_ +
      '/android.emulation.control.EmulatorController/getGps',
      request,
      metadata || {},
      methodInfo_EmulatorController_getGps);
};


/**
 * @const
 * @type {!grpc.web.AbstractClientBase.MethodInfo<
 *   !proto.android.emulation.control.GpsState,
 *   !proto.android.emulation.control.GpsState>}
 */
const methodInfo_EmulatorController_setGps = new grpc.web.AbstractClientBase.MethodInfo(
  proto.android.emulation.control.GpsState,
  /** @param {!proto.android.emulation.control.GpsState} request */
  function(request) {
    return request.serializeBinary();
  },
  proto.android.emulation.control.GpsState.deserializeBinary
);


/**
 * @param {!proto.android.emulation.control.GpsState} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @param {function(?grpc.web.Error, ?proto.android.emulation.control.GpsState)}
 *     callback The callback function(error, response)
 * @return {!grpc.web.ClientReadableStream<!proto.android.emulation.control.GpsState>|undefined}
 *     The XHR Node Readable Stream
 */
proto.android.emulation.control.EmulatorControllerClient.prototype.setGps =
    function(request, metadata, callback) {
  return this.client_.rpcCall(this.hostname_ +
      '/android.emulation.control.EmulatorController/setGps',
      request,
      metadata || {},
      methodInfo_EmulatorController_setGps,
      callback);
};


/**
 * @param {!proto.android.emulation.control.GpsState} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @return {!Promise<!proto.android.emulation.control.GpsState>}
 *     A native promise that resolves to the response
 */
proto.android.emulation.control.EmulatorControllerPromiseClient.prototype.setGps =
    function(request, metadata) {
  return this.client_.unaryCall(this.hostname_ +
      '/android.emulation.control.EmulatorController/setGps',
      request,
      metadata || {},
      methodInfo_EmulatorController_setGps);
};


/**
 * @const
 * @type {!grpc.web.AbstractClientBase.MethodInfo<
 *   !proto.android.emulation.control.FingerprintEvent,
 *   !proto.google.protobuf.Empty>}
 */
const methodInfo_EmulatorController_sendFingerprint = new grpc.web.AbstractClientBase.MethodInfo(
  google_protobuf_empty_pb.Empty,
  /** @param {!proto.android.emulation.control.FingerprintEvent} request */
  function(request) {
    return request.serializeBinary();
  },
  google_protobuf_empty_pb.Empty.deserializeBinary
);


/**
 * @param {!proto.android.emulation.control.FingerprintEvent} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @param {function(?grpc.web.Error, ?proto.google.protobuf.Empty)}
 *     callback The callback function(error, response)
 * @return {!grpc.web.ClientReadableStream<!proto.google.protobuf.Empty>|undefined}
 *     The XHR Node Readable Stream
 */
proto.android.emulation.control.EmulatorControllerClient.prototype.sendFingerprint =
    function(request, metadata, callback) {
  return this.client_.rpcCall(this.hostname_ +
      '/android.emulation.control.EmulatorController/sendFingerprint',
      request,
      metadata || {},
      methodInfo_EmulatorController_sendFingerprint,
      callback);
};


/**
 * @param {!proto.android.emulation.control.FingerprintEvent} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @return {!Promise<!proto.google.protobuf.Empty>}
 *     A native promise that resolves to the response
 */
proto.android.emulation.control.EmulatorControllerPromiseClient.prototype.sendFingerprint =
    function(request, metadata) {
  return this.client_.unaryCall(this.hostname_ +
      '/android.emulation.control.EmulatorController/sendFingerprint',
      request,
      metadata || {},
      methodInfo_EmulatorController_sendFingerprint);
};


/**
 * @const
 * @type {!grpc.web.AbstractClientBase.MethodInfo<
 *   !proto.android.emulation.control.KeyboardEvent,
 *   !proto.google.protobuf.Empty>}
 */
const methodInfo_EmulatorController_sendKey = new grpc.web.AbstractClientBase.MethodInfo(
  google_protobuf_empty_pb.Empty,
  /** @param {!proto.android.emulation.control.KeyboardEvent} request */
  function(request) {
    return request.serializeBinary();
  },
  google_protobuf_empty_pb.Empty.deserializeBinary
);


/**
 * @param {!proto.android.emulation.control.KeyboardEvent} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @param {function(?grpc.web.Error, ?proto.google.protobuf.Empty)}
 *     callback The callback function(error, response)
 * @return {!grpc.web.ClientReadableStream<!proto.google.protobuf.Empty>|undefined}
 *     The XHR Node Readable Stream
 */
proto.android.emulation.control.EmulatorControllerClient.prototype.sendKey =
    function(request, metadata, callback) {
  return this.client_.rpcCall(this.hostname_ +
      '/android.emulation.control.EmulatorController/sendKey',
      request,
      metadata || {},
      methodInfo_EmulatorController_sendKey,
      callback);
};


/**
 * @param {!proto.android.emulation.control.KeyboardEvent} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @return {!Promise<!proto.google.protobuf.Empty>}
 *     A native promise that resolves to the response
 */
proto.android.emulation.control.EmulatorControllerPromiseClient.prototype.sendKey =
    function(request, metadata) {
  return this.client_.unaryCall(this.hostname_ +
      '/android.emulation.control.EmulatorController/sendKey',
      request,
      metadata || {},
      methodInfo_EmulatorController_sendKey);
};


/**
 * @const
 * @type {!grpc.web.AbstractClientBase.MethodInfo<
 *   !proto.android.emulation.control.TouchEvent,
 *   !proto.google.protobuf.Empty>}
 */
const methodInfo_EmulatorController_sendTouch = new grpc.web.AbstractClientBase.MethodInfo(
  google_protobuf_empty_pb.Empty,
  /** @param {!proto.android.emulation.control.TouchEvent} request */
  function(request) {
    return request.serializeBinary();
  },
  google_protobuf_empty_pb.Empty.deserializeBinary
);


/**
 * @param {!proto.android.emulation.control.TouchEvent} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @param {function(?grpc.web.Error, ?proto.google.protobuf.Empty)}
 *     callback The callback function(error, response)
 * @return {!grpc.web.ClientReadableStream<!proto.google.protobuf.Empty>|undefined}
 *     The XHR Node Readable Stream
 */
proto.android.emulation.control.EmulatorControllerClient.prototype.sendTouch =
    function(request, metadata, callback) {
  return this.client_.rpcCall(this.hostname_ +
      '/android.emulation.control.EmulatorController/sendTouch',
      request,
      metadata || {},
      methodInfo_EmulatorController_sendTouch,
      callback);
};


/**
 * @param {!proto.android.emulation.control.TouchEvent} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @return {!Promise<!proto.google.protobuf.Empty>}
 *     A native promise that resolves to the response
 */
proto.android.emulation.control.EmulatorControllerPromiseClient.prototype.sendTouch =
    function(request, metadata) {
  return this.client_.unaryCall(this.hostname_ +
      '/android.emulation.control.EmulatorController/sendTouch',
      request,
      metadata || {},
      methodInfo_EmulatorController_sendTouch);
};


/**
 * @const
 * @type {!grpc.web.AbstractClientBase.MethodInfo<
 *   !proto.android.emulation.control.MouseEvent,
 *   !proto.google.protobuf.Empty>}
 */
const methodInfo_EmulatorController_sendMouse = new grpc.web.AbstractClientBase.MethodInfo(
  google_protobuf_empty_pb.Empty,
  /** @param {!proto.android.emulation.control.MouseEvent} request */
  function(request) {
    return request.serializeBinary();
  },
  google_protobuf_empty_pb.Empty.deserializeBinary
);


/**
 * @param {!proto.android.emulation.control.MouseEvent} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @param {function(?grpc.web.Error, ?proto.google.protobuf.Empty)}
 *     callback The callback function(error, response)
 * @return {!grpc.web.ClientReadableStream<!proto.google.protobuf.Empty>|undefined}
 *     The XHR Node Readable Stream
 */
proto.android.emulation.control.EmulatorControllerClient.prototype.sendMouse =
    function(request, metadata, callback) {
  return this.client_.rpcCall(this.hostname_ +
      '/android.emulation.control.EmulatorController/sendMouse',
      request,
      metadata || {},
      methodInfo_EmulatorController_sendMouse,
      callback);
};


/**
 * @param {!proto.android.emulation.control.MouseEvent} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @return {!Promise<!proto.google.protobuf.Empty>}
 *     A native promise that resolves to the response
 */
proto.android.emulation.control.EmulatorControllerPromiseClient.prototype.sendMouse =
    function(request, metadata) {
  return this.client_.unaryCall(this.hostname_ +
      '/android.emulation.control.EmulatorController/sendMouse',
      request,
      metadata || {},
      methodInfo_EmulatorController_sendMouse);
};


/**
 * @const
 * @type {!grpc.web.AbstractClientBase.MethodInfo<
 *   !proto.android.emulation.control.RotaryEvent,
 *   !proto.google.protobuf.Empty>}
 */
const methodInfo_EmulatorController_sendRotary = new grpc.web.AbstractClientBase.MethodInfo(
  google_protobuf_empty_pb.Empty,
  /** @param {!proto.android.emulation.control.RotaryEvent} request */
  function(request) {
    return request.serializeBinary();
  },
  google_protobuf_empty_pb.Empty.deserializeBinary
);


/**
 * @param {!proto.android.emulation.control.RotaryEvent} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @param {function(?grpc.web.Error, ?proto.google.protobuf.Empty)}
 *     callback The callback function(error, response)
 * @return {!grpc.web.ClientReadableStream<!proto.google.protobuf.Empty>|undefined}
 *     The XHR Node Readable Stream
 */
proto.android.emulation.control.EmulatorControllerClient.prototype.sendRotary =
    function(request, metadata, callback) {
  return this.client_.rpcCall(this.hostname_ +
      '/android.emulation.control.EmulatorController/sendRotary',
      request,
      metadata || {},
      methodInfo_EmulatorController_sendRotary,
      callback);
};


/**
 * @param {!proto.android.emulation.control.RotaryEvent} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @return {!Promise<!proto.google.protobuf.Empty>}
 *     A native promise that resolves to the response
 */
proto.android.emulation.control.EmulatorControllerPromiseClient.prototype.sendRotary =
    function(request, metadata) {
  return this.client_.unaryCall(this.hostname_ +
      '/android.emulation.control.EmulatorController/sendRotary',
      request,
      metadata || {},
      methodInfo_EmulatorController_sendRotary);
};


/**
 * @const
 * @type {!grpc.web.AbstractClientBase.MethodInfo<
 *   !proto.google.protobuf.Empty,
 *   !proto.android.emulation.control.VmConfiguration>}
 */
const methodInfo_EmulatorController_getVmConfiguration = new grpc.web.AbstractClientBase.MethodInfo(
  proto.android.emulation.control.VmConfiguration,
  /** @param {!proto.google.protobuf.Empty} request */
  function(request) {
    return request.serializeBinary();
  },
  proto.android.emulation.control.VmConfiguration.deserializeBinary
);


/**
 * @param {!proto.google.protobuf.Empty} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @param {function(?grpc.web.Error, ?proto.android.emulation.control.VmConfiguration)}
 *     callback The callback function(error, response)
 * @return {!grpc.web.ClientReadableStream<!proto.android.emulation.control.VmConfiguration>|undefined}
 *     The XHR Node Readable Stream
 */
proto.android.emulation.control.EmulatorControllerClient.prototype.getVmConfiguration =
    function(request, metadata, callback) {
  return this.client_.rpcCall(this.hostname_ +
      '/android.emulation.control.EmulatorController/getVmConfiguration',
      request,
      metadata || {},
      methodInfo_EmulatorController_getVmConfiguration,
      callback);
};


/**
 * @param {!proto.google.protobuf.Empty} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @return {!Promise<!proto.android.emulation.control.VmConfiguration>}
 *     A native promise that resolves to the response
 */
proto.android.emulation.control.EmulatorControllerPromiseClient.prototype.getVmConfiguration =
    function(request, metadata) {
  return this.client_.unaryCall(this.hostname_ +
      '/android.emulation.control.EmulatorController/getVmConfiguration',
      request,
      metadata || {},
      methodInfo_EmulatorController_getVmConfiguration);
};


/**
 * @const
 * @type {!grpc.web.AbstractClientBase.MethodInfo<
 *   !proto.android.emulation.control.ImageFormat,
 *   !proto.android.emulation.control.Image>}
 */
const methodInfo_EmulatorController_getScreenshot = new grpc.web.AbstractClientBase.MethodInfo(
  proto.android.emulation.control.Image,
  /** @param {!proto.android.emulation.control.ImageFormat} request */
  function(request) {
    return request.serializeBinary();
  },
  proto.android.emulation.control.Image.deserializeBinary
);


/**
 * @param {!proto.android.emulation.control.ImageFormat} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @param {function(?grpc.web.Error, ?proto.android.emulation.control.Image)}
 *     callback The callback function(error, response)
 * @return {!grpc.web.ClientReadableStream<!proto.android.emulation.control.Image>|undefined}
 *     The XHR Node Readable Stream
 */
proto.android.emulation.control.EmulatorControllerClient.prototype.getScreenshot =
    function(request, metadata, callback) {
  return this.client_.rpcCall(this.hostname_ +
      '/android.emulation.control.EmulatorController/getScreenshot',
      request,
      metadata || {},
      methodInfo_EmulatorController_getScreenshot,
      callback);
};


/**
 * @param {!proto.android.emulation.control.ImageFormat} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @return {!Promise<!proto.android.emulation.control.Image>}
 *     A native promise that resolves to the response
 */
proto.android.emulation.control.EmulatorControllerPromiseClient.prototype.getScreenshot =
    function(request, metadata) {
  return this.client_.unaryCall(this.hostname_ +
      '/android.emulation.control.EmulatorController/getScreenshot',
      request,
      metadata || {},
      methodInfo_EmulatorController_getScreenshot);
};


/**
 * @const
 * @type {!grpc.web.AbstractClientBase.MethodInfo<
 *   !proto.android.emulation.control.LogMessage,
 *   !proto.android.emulation.control.LogMessage>}
 */
const methodInfo_EmulatorController_getLogcat = new grpc.web.AbstractClientBase.MethodInfo(
  proto.android.emulation.control.LogMessage,
  /** @param {!proto.android.emulation.control.LogMessage} request */
  function(request) {
    return request.serializeBinary();
  },
  proto.android.emulation.control.LogMessage.deserializeBinary
);


/**
 * @param {!proto.android.emulation.control.LogMessage} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @param {function(?grpc.web.Error, ?proto.android.emulation.control.LogMessage)}
 *     callback The callback function(error, response)
 * @return {!grpc.web.ClientReadableStream<!proto.android.emulation.control.LogMessage>|undefined}
 *     The XHR Node Readable Stream
 */
proto.android.emulation.control.EmulatorControllerClient.prototype.getLogcat =
    function(request, metadata, callback) {
  return this.client_.rpcCall(this.hostname_ +
      '/android.emulation.control.EmulatorController/getLogcat',
      request,
      metadata || {},
      methodInfo_EmulatorController_getLogcat,
      callback);
};


/**
 * @param {!proto.android.emulation.control.LogMessage} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @return {!Promise<!proto.android.emulation.control.LogMessage>}
 *     A native promise that resolves to the response
 */
proto.android.emulation.control.EmulatorControllerPromiseClient.prototype.getLogcat =
    function(request, metadata) {
  return this.client_.unaryCall(this.hostname_ +
      '/android.emulation.control.EmulatorController/getLogcat',
      request,
      metadata || {},
      methodInfo_EmulatorController_getLogcat);
};


/**
 * @const
 * @type {!grpc.web.AbstractClientBase.MethodInfo<
 *   !proto.android.emulation.control.LogMessage,
 *   !proto.android.emulation.control.LogMessage>}
 */
const methodInfo_EmulatorController_streamLogcat = new grpc.web.AbstractClientBase.MethodInfo(
  proto.android.emulation.control.LogMessage,
  /** @param {!proto.android.emulation.control.LogMessage} request */
  function(request) {
    return request.serializeBinary();
  },
  proto.android.emulation.control.LogMessage.deserializeBinary
);


/**
 * @param {!proto.android.emulation.control.LogMessage} request The request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @return {!grpc.web.ClientReadableStream<!proto.android.emulation.control.LogMessage>}
 *     The XHR Node Readable Stream
 */
proto.android.emulation.control.EmulatorControllerClient.prototype.streamLogcat =
    function(request, metadata) {
  return this.client_.serverStreaming(this.hostname_ +
      '/android.emulation.control.EmulatorController/streamLogcat',
      request,
      metadata || {},
      methodInfo_EmulatorController_streamLogcat);
};


/**
 * @param {!proto.android.emulation.control.LogMessage} request The request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @return {!grpc.web.ClientReadableStream<!proto.android.emulation.control.LogMessage>}
 *     The XHR Node Readable Stream
 */
proto.android.emulation.control.EmulatorControllerPromiseClient.prototype.streamLogcat =
    function(request, metadata) {
  return this.client_.serverStreaming(this.hostname_ +
      '/android.emulation.control.EmulatorController/streamLogcat',
      request,
      metadata || {},
      methodInfo_EmulatorController_streamLogcat);
};


/**
 * @const
 * @type {!grpc.web.AbstractClientBase.MethodInfo<
 *   !proto.android.emulation.control.TelephoneOperation,
 *   !proto.android.emulation.control.TelephoneResponse>}
 */
const methodInfo_EmulatorController_usePhone = new grpc.web.AbstractClientBase.MethodInfo(
  proto.android.emulation.control.TelephoneResponse,
  /** @param {!proto.android.emulation.control.TelephoneOperation} request */
  function(request) {
    return request.serializeBinary();
  },
  proto.android.emulation.control.TelephoneResponse.deserializeBinary
);


/**
 * @param {!proto.android.emulation.control.TelephoneOperation} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @param {function(?grpc.web.Error, ?proto.android.emulation.control.TelephoneResponse)}
 *     callback The callback function(error, response)
 * @return {!grpc.web.ClientReadableStream<!proto.android.emulation.control.TelephoneResponse>|undefined}
 *     The XHR Node Readable Stream
 */
proto.android.emulation.control.EmulatorControllerClient.prototype.usePhone =
    function(request, metadata, callback) {
  return this.client_.rpcCall(this.hostname_ +
      '/android.emulation.control.EmulatorController/usePhone',
      request,
      metadata || {},
      methodInfo_EmulatorController_usePhone,
      callback);
};


/**
 * @param {!proto.android.emulation.control.TelephoneOperation} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @return {!Promise<!proto.android.emulation.control.TelephoneResponse>}
 *     A native promise that resolves to the response
 */
proto.android.emulation.control.EmulatorControllerPromiseClient.prototype.usePhone =
    function(request, metadata) {
  return this.client_.unaryCall(this.hostname_ +
      '/android.emulation.control.EmulatorController/usePhone',
      request,
      metadata || {},
      methodInfo_EmulatorController_usePhone);
};


/**
 * @const
 * @type {!grpc.web.AbstractClientBase.MethodInfo<
 *   !proto.google.protobuf.Empty,
 *   !proto.android.emulation.control.RtcId>}
 */
const methodInfo_EmulatorController_requestRtcStream = new grpc.web.AbstractClientBase.MethodInfo(
  proto.android.emulation.control.RtcId,
  /** @param {!proto.google.protobuf.Empty} request */
  function(request) {
    return request.serializeBinary();
  },
  proto.android.emulation.control.RtcId.deserializeBinary
);


/**
 * @param {!proto.google.protobuf.Empty} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @param {function(?grpc.web.Error, ?proto.android.emulation.control.RtcId)}
 *     callback The callback function(error, response)
 * @return {!grpc.web.ClientReadableStream<!proto.android.emulation.control.RtcId>|undefined}
 *     The XHR Node Readable Stream
 */
proto.android.emulation.control.EmulatorControllerClient.prototype.requestRtcStream =
    function(request, metadata, callback) {
  return this.client_.rpcCall(this.hostname_ +
      '/android.emulation.control.EmulatorController/requestRtcStream',
      request,
      metadata || {},
      methodInfo_EmulatorController_requestRtcStream,
      callback);
};


/**
 * @param {!proto.google.protobuf.Empty} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @return {!Promise<!proto.android.emulation.control.RtcId>}
 *     A native promise that resolves to the response
 */
proto.android.emulation.control.EmulatorControllerPromiseClient.prototype.requestRtcStream =
    function(request, metadata) {
  return this.client_.unaryCall(this.hostname_ +
      '/android.emulation.control.EmulatorController/requestRtcStream',
      request,
      metadata || {},
      methodInfo_EmulatorController_requestRtcStream);
};


/**
 * @const
 * @type {!grpc.web.AbstractClientBase.MethodInfo<
 *   !proto.android.emulation.control.JsepMsg,
 *   !proto.google.protobuf.Empty>}
 */
const methodInfo_EmulatorController_sendJsepMessage = new grpc.web.AbstractClientBase.MethodInfo(
  google_protobuf_empty_pb.Empty,
  /** @param {!proto.android.emulation.control.JsepMsg} request */
  function(request) {
    return request.serializeBinary();
  },
  google_protobuf_empty_pb.Empty.deserializeBinary
);


/**
 * @param {!proto.android.emulation.control.JsepMsg} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @param {function(?grpc.web.Error, ?proto.google.protobuf.Empty)}
 *     callback The callback function(error, response)
 * @return {!grpc.web.ClientReadableStream<!proto.google.protobuf.Empty>|undefined}
 *     The XHR Node Readable Stream
 */
proto.android.emulation.control.EmulatorControllerClient.prototype.sendJsepMessage =
    function(request, metadata, callback) {
  return this.client_.rpcCall(this.hostname_ +
      '/android.emulation.control.EmulatorController/sendJsepMessage',
      request,
      metadata || {},
      methodInfo_EmulatorController_sendJsepMessage,
      callback);
};


/**
 * @param {!proto.android.emulation.control.JsepMsg} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @return {!Promise<!proto.google.protobuf.Empty>}
 *     A native promise that resolves to the response
 */
proto.android.emulation.control.EmulatorControllerPromiseClient.prototype.sendJsepMessage =
    function(request, metadata) {
  return this.client_.unaryCall(this.hostname_ +
      '/android.emulation.control.EmulatorController/sendJsepMessage',
      request,
      metadata || {},
      methodInfo_EmulatorController_sendJsepMessage);
};


/**
 * @const
 * @type {!grpc.web.AbstractClientBase.MethodInfo<
 *   !proto.android.emulation.control.RtcId,
 *   !proto.android.emulation.control.JsepMsg>}
 */
const methodInfo_EmulatorController_receiveJsepMessage = new grpc.web.AbstractClientBase.MethodInfo(
  proto.android.emulation.control.JsepMsg,
  /** @param {!proto.android.emulation.control.RtcId} request */
  function(request) {
    return request.serializeBinary();
  },
  proto.android.emulation.control.JsepMsg.deserializeBinary
);


/**
 * @param {!proto.android.emulation.control.RtcId} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @param {function(?grpc.web.Error, ?proto.android.emulation.control.JsepMsg)}
 *     callback The callback function(error, response)
 * @return {!grpc.web.ClientReadableStream<!proto.android.emulation.control.JsepMsg>|undefined}
 *     The XHR Node Readable Stream
 */
proto.android.emulation.control.EmulatorControllerClient.prototype.receiveJsepMessage =
    function(request, metadata, callback) {
  return this.client_.rpcCall(this.hostname_ +
      '/android.emulation.control.EmulatorController/receiveJsepMessage',
      request,
      metadata || {},
      methodInfo_EmulatorController_receiveJsepMessage,
      callback);
};


/**
 * @param {!proto.android.emulation.control.RtcId} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @return {!Promise<!proto.android.emulation.control.JsepMsg>}
 *     A native promise that resolves to the response
 */
proto.android.emulation.control.EmulatorControllerPromiseClient.prototype.receiveJsepMessage =
    function(request, metadata) {
  return this.client_.unaryCall(this.hostname_ +
      '/android.emulation.control.EmulatorController/receiveJsepMessage',
      request,
      metadata || {},
      methodInfo_EmulatorController_receiveJsepMessage);
};


module.exports = proto.android.emulation.control;

