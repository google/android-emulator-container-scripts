# Known Issues

Here are a list of things that we have seen with potential workarounds:

## Why can't I use an image before O?

Releases before O are using an older linux kernel (3.10). This version of the
linux kernel has some issues that are under [active
investigation](https://issuetracker.google.com/issues/140881613) for X86_64 images.


## Unable to find emu-docker

Some people have reported issues around launching `emu-docker`.
[Issue #30](https://github.com/google/android-emulator-container-scripts/issues/30).
The easiest way to resolve this is to run the project in a virtual environment.
The virtual environment can be activated as follows:

```sh
source ./configure.sh
```

This will create a virtual environment and activate it for you. This will make
sure everything is isolated and you should be able to launch `emu-docker`.

## Exceptions when trying to create the docker container:

If you see an exception along the following lines:

```python
Traceback (most recent call last):
  File "/tmp/android-emulator-container-scripts/emu/docker_device.py", line 78, in create_container
    logging.info(api_client.version())
  File "/tmp/android-emulator-container-scripts/venv/lib/python3.5/site-packages/docker-4.0.2-py3.5.egg/dn
    return self._result(self._get(url), json=True)
  File "/tmp/android-emulator-container-scripts/venv/lib/python3.5/site-packages/docker-4.0.2-py3.5.egg/dr
    return f(self, *args, **kwargs)
  File "/tmp/android-emulator-container-scripts/venv/lib/python3.5/site-packages/docker-4.0.2-py3.5.egg/dt
    return self.get(url, **self._set_request_timeout(kwargs))
  File "/tmp/android-emulator-container-scripts/venv/lib/python3.5/site-packages/requests-2.22.0-py3.5.egt
    return self.request('GET', url, **kwargs)
  File "/tmp/android-emulator-container-scripts/venv/lib/python3.5/site-packages/requests-2.22.0-py3.5.egt
    resp = self.send(prep, **send_kwargs)
  File "/tmp/android-emulator-container-scripts/venv/lib/python3.5/site-packages/requests-2.22.0-py3.5.egd
    r = adapter.send(request, **kwargs)
  File "/tmp/android-emulator-container-scripts/venv/lib/python3.5/site-packages/requests-2.22.0-py3.5.egd
    raise ConnectionError(err, request=request)
requests.exceptions.ConnectionError: ('Connection aborted.', PermissionError(13, 'Permission denied'))
```
This means you do not have permission to interact with docker. You must enable sudoless docker, follow the
steps outlined [here](https://docs.docker.com/install/linux/linux-postinstall/)

## Exception around ADB

If you see an exception along the following lines:

```python
Traceback (most recent call last):
  File "/tmp/android-emulator-container-scripts/venv/bin/emu-docker", line 11, in <module>
    load_entry_point('emu-docker', 'console_scripts', 'emu-docker')()
  File "/tmp/android-emulator-container-scripts/emu/emu_docker.py", line 123, in main
    args.func(args)
  File "/tmp/android-emulator-container-scripts/emu/emu_docker.py", line 48, in create_docker_image_intere
    device.create_docker_file(args.extra)
  File "/tmp/android-emulator-container-scripts/emu/docker_device.py", line 119, in create_docker_file
    raise IOError(errno.ENOENT, "Unable to find ADB below $ANDROID_SDK_ROOT or on the path!")
FileNotFoundError: [Errno 2] Unable to find ADB below $ANDROID_SDK_ROOT or on the path!
```

You will need to install adb.

## Exceptions when providing wrong zipfiles

If you seen an exception along the following lines:

```python
Traceback (most recent call last):
  File "/tmp/android-emulator-container-scripts/venv/bin/emu-docker", line 11, in <module>
    load_entry_point('emu-docker', 'console_scripts', 'emu-docker')()
  File "/tmp/android-emulator-container-scripts/emu/emu_docker.py", line 159, in main
    args.func(args)
  File "/tmp/android-emulator-container-scripts/emu/emu_docker.py", line 44, in create_docker_image
    raise Exception("{} is not a zip file with a system image".format(imgzip))
Exception: emulator-29.2.8.zip is not a zip file with a system image
```

You likely provided the parameters in the incorrect order.

## The container suddenly stopped and I cannot restart it.

It is possible that the emulator crashes or terminates unexpectedly. In this
case it is possible that the container gets into a corrupted state.

If this is the case you will have to delete the container:

```sh
docker rm -f CONTAINER_ID
```

where `CONTAINER_ID` is the id of the emulator container.

## I am not seeing any video in the demo when selecting webrtc

1. Click the png button. This will not use webrtc but request individual
   screenshots from the emulator. If this works you learn the following:

    - The emulator is running.
    - The gRPC endpoint is properly working.

    If the button does not show the emulator then you are possibly running an
    older emulator without gRPC support. Make sure you use the latest canary
    build.

2. I do see video when using the png button.

    - Click the `webrtc` button. Make sure no video is showing.
    - Check the JavaScript console log.

    If you only see: `handleJsepMessage: {"start":{}}` then the video bridge is
    not running as expected. You could consult the logs for more info:  `docker
    logs docker_emulator_1 | egrep "pulse:|video:|version:"`

If you see something along the lines of:

```javascript
handleJsepMessage: {"start":{}}
jsep_protocol_driver.js:124 handleJsepMessage: {"sdp":"i...
label:emulator_video_stream\r\n","type":"offer"}
jsep_protocol_driver.js:76 handlePeerConnectionTrack: connecting [object
RTCTrackEvent]
webrtc_view.js:42 Connecting video stream: [object HTMLVideoElement]:0
jsep_protocol_driver.js:124 handleJsepMessage:
{"candidate":"candidate:3808623835 1 udp 2122260223 172.20.0.4 38033 typ
host generation 0 ufrag kyFW network-id 1","sdpMLineIndex":0,"sdpMid":"0"}
jsep_protocol_driver.js:124 handleJsepMessage:
{"candidate":"candidate:2325047 1 udp 1686052607 104.132.0.73 59912 typ
srflx raddr 172.20.0.4 rport 38033 generation 0 ufrag kyFW network-id
1","sdpMLineIndex":0,"sdpMid":"0"}
webrtc_view.js:50 Automatic playback started!
```

You could be in a situation where
a [TURN](https://en.wikipedia.org/wiki/Traversal_Using_Relays_around_NAT) is
needed. This is usually only the case when you are in a restricted network.
You can launch the emulator `$ANDROID_SDK_ROOT/emulator/emulator
-help-turncfg` under linux to learn how to configure turn.  You can pass use
`emu_docker create --help` to learn how to pass the `--turncfg` flag to the
emulator.


## Unable to launch docker image

If you are seeing exceptions during the creation of a docker image directly from python, such as these:

```python
Traceback (most recent call last):
  File "....python3.6/site-packages/urllib3/connectionpool.py", line 600, in urlopen
    chunked=chunked)
  File ".../python3.6/site-packages/urllib3/connectionpool.py", line 354, in _make_request
    conn.request(method, url, **httplib_request_kw)
  File "/usr/lib/python3.6/http/client.py", line 1239, in request
    self._send_request(method, url, body, headers, encode_chunked)
  File "/usr/lib/python3.6/http/client.py", line 1285, in _send_request
    self.endheaders(body, encode_chunked=encode_chunked)
  File "/usr/lib/python3.6/http/client.py", line 1234, in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
  File "/usr/lib/python3.6/http/client.py", line 1065, in _send_output
    self.send(chunk)
  File "/usr/lib/python3.6/http/client.py", line 986, in send
    self.sock.sendall(data)
ConnectionResetError: [Errno 104] Connection reset by peer
```

One of the possibilities is that you have not properly configured your credential helpers. Launch withe `-v` flag to
see how docker tries to authenticate to your local service.

## Credential errors with docker-compose

We have seen errors when running docker-compose from a virtual environment.

The easiest solution is not to use docker-compose from a virtual environment.

## Trouble compiling protoc plugins with Homebrew

It is possible that `pkgconfig` is not able to find the proper location of your protobuf libraries.
This can happen if you are using homebrew with uncommon install location. The easiest way around this
is to explicitly set the pkg-config directory to point to your libprotobuf description. For example:

```sh
export PKG_CONFIG_PATH=$PKG_CONFIG_PATH:$(find $(brew --prefix) -name 'pkgconfig' -print | grep protobuf)
```

Now you can install the protoc-plugin as follows:

```sh
cd js/protoc-plugin
make
sudo make install
```
