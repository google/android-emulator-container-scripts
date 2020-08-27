# Using a TURN server

This document describes how you can use a turn server and includes a simple
example of how you could deploy your own. You would need a turn server if you
are running the emulator in network that is not publicly accessible.

To enable turn you must have the following:

- A publicly accessible turn server.
- A mechanism to create a JSON turn configuration snippet the emulator can give
  to the browser clients.

Keep in mind that a savvy user could extract this snippet from the browser. Do not hand out permanent valid configurations
if you do not trust your end users. A malicious user could use your TURN server for their own relay.

## Quick start turn server.

In this example we will use [coturn](https://github.com/coturn/coturn) as our turn server that uses a fixed set of credentials. You can use this configuration if you trust your users, or if you quickly want to test something.

1.  Launch the turn server that is publicly accessible (say my.turn.org):

    In the example below we are using an _insecure_ turn server. You should at least
    provide a configuration file with passwords if you are going to deploy this.

    ```sh
    export TURN_SERVER="localhost" # This should be your real host name!
    turnserver -v -n --log-file=stdout  -r $TURN_SERVER
    ```

    You can find details on using long term credentials in turn [here](https://github.com/coturn/coturn/wiki/README).

2.  Create the json snippet, that provides access:

    ```js
    {
      "iceServers": [
        {
          "urls": "turn:$TURN_SERVER",
          "username": "webrtc",
          "credential": "turnpassword",
        },
      ];
    }
    ```

    Note that the username and password depend on how you configured your turn server and
    are not needed if you are running an insecure server.

3.  Launch the emulator container with the turncfg flag with the snippet as a single line:

    ```sh
    export SNIPPET="{\"iceServers\":[{\"urls\":\"turn:$TURN_SERVER\",\"username\":\"webrtc\",\"credential\":\"turnpassword\"}]}"
    docker run  \
     -e ADBKEY="$(cat ~/.android/adbkey)" \
     -e TURN="printf $SNIPPET" \
     --device /dev/kvm  \
     --publish 8554:8554/tcp \
     --publish 5555:5555/tcp ${CONTAINER_ID}
    ```

    If you wish to confirm that this is working properly you can check the docker logs for a line like this:

    ```sh
    docker logs my_container_id | grep Switchboard.cpp
    video: (Switchboard.cpp:264): Sending {"msg":"{\"start\":{\"iceServers\":[{\"credential\":\"turnpassword\",\"urls\":\"turn:\",\"username\":\"webrtc\"}]}}","topic":"c6965c12-8b72-45c3-bc7d-f8143488382a"}
    ```

## Quick start using secure turn with temporary credentials

In this example we will use [coturn](https://github.com/coturn/coturn) as our turn server, and we will use a simple python rest api to provide us with a secure configuration. The emulator will call the rest api which in turn will create a valid configuration that the turn server accepts.

For this you will need:

- A public coTURN server.
- A shared secret between the coTURN server and the Python REST api
- A shared secret between the Python REST api and the emulator.
- [jq](https://stedolan.github.io/jq/), used to quickly test your config
- [coturn](https://github.com/coturn/coturn), you will use the utilities to test and the server.

1. Launch the Python REST api server. This does not have to be public, but must
   be accessible by the emulator (say turn_key.provider.org)

   ```sh
   export API_KEY="a_secret_the_emulator_needs"
   export SECRET="a_secret_that_the_turn_server_needs"
   python turn.py --turn_secret $SECRET --api_key $API_KEY --port 8080
   ```

   Make sure that the api server works and is accessible, for example

   ```sh
   export API_SERVER=http://turn_key.provider.org
   curl -s $API_SERVER/turn/localhost?apiKey=$API_KEY
   ```

   Should return something like this:

   ```js
   {"iceServers":[{"credential":"dFSc+Cg119PBHBx+qodUPI/19ic=","urls":["turn:localhost"],"username":"1598484959:someone"}]}
   ```

2. Launch the turn server that is publicly accessible (say my.turn.org):

   ```sh
   export TURN_SERVER="localhost" # This should be your real host name!
   turnserver -v -n --log-file=stdout \
        --use-auth-secret --static-auth-secret=$SECRET -r $TURN_SERVER
   ```

   Make sure your turn server is properly configured by making sure
   you can connect with the generated JSON config from the previous step:

   Using [jq](https://stedolan.github.io/jq/) we can construct our test:

   ```sh
   curl -s "http://localhost:8123/turn/localhost?apiKey=$API_KEY" | \
   jq '.iceServers[0] | "turnutils_uclient -w \(.credential) -u \(.username) $TURN_SERVER"'
   ```

   Now copy paste the result and execute the command, if all went well you should see results.
   For example:

   ```sh
   $ turnutils_uclient -w GH7ON8EceVvLtr96vSIB6unYBRM= -u 1598489324:someone   localhost

   0: Total connect time is 0
   1: start_mclient: msz=2, tot_send_msgs=0, tot_recv_msgs=0, tot_send_bytes ~ 0, tot_recv_bytes ~ 0
   2: start_mclient: msz=2, tot_send_msgs=4, tot_recv_msgs=0, tot_send_bytes ~ 400, tot_recv_bytes ~ 0
   3: start_mclient: msz=2, tot_send_msgs=5, tot_recv_msgs=0, tot_send_bytes ~ 500, tot_recv_bytes ~ 0
   4: start_mclient: msz=2, tot_send_msgs=5, tot_recv_msgs=0, tot_send_bytes ~ 500, tot_recv_bytes ~ 0
   5: start_mclient: msz=2, tot_send_msgs=5, tot_recv_msgs=0, tot_send_bytes ~ 500, tot_recv_bytes ~ 0
   ```

   Congratulations! You have a secure working turn server.

3. Launch the emulator container with the turncfg flag:

   ```sh
   docker run  \
    -e ADBKEY="$(cat ~/.android/adbkey)" \
    -e TURN="curl -s $TURN_API/turn/$TURN_SERVER\?apiKey=$API_KEY" \
    --device /dev/kvm  \
    --publish 8554:8554/tcp \
    --publish 5555:5555/tcp ${CONTAINER_ID}
   ```

   You should now be able to launch the web application which should make use of your turn service.
   If all went well you should see loglines such as these:

   ```
   emulator: INFO: RtcService.cpp:98: RtcPacket: id { guid: "6da5cc46-7afc-4409-a77c-315dfe418f83" } message: "{\"start\":{\"iceServers\":[{\"credential\":\"mzddNrUmJcvp9Xg4q1ttzasd8Qk=\",\"urls\":[\"turn:localhost\"],\"username\":\"1598489788:someone\"}]}}"
   ```

   The emulator is informing your client to use your turn server

## Custom configurations

The emulator has support for turn if you have a command that does the following:

- Produce a result on stdout.
- Produce a result within 1000 ms.
- Produce a valid [JSON RTCConfiguration object](https://developer.mozilla.org/en-US/docs/Web/API/RTCConfiguration).
- That contains at least an "iceServers" array.
- The exit value should be 0 on success

This command can be passed in with the -turncfg parameter to the emulator. For example:

```sh
emulator -grpc 8554 -turncfg 'printf {"iceServers":[{"urls":["stun:stun.l.google.com:19302"]}]}'
```

This will use the standard stun server that Google provides. In general we support two approaches out of the box:

- A static configuration: You can use `printf` as shown above to produce the static snippet.
- A dynamic configuration: The emulator container ships with `curl`, which can be used to obtain a snippet.
  Make sure to pass in the `-s` flag to keep curl silent.

Both approaches can meet the requirements mentioned above.

### Enable turn in containers.

There are two ways in which we can embed the turn configuration inside the emulator:

- **During run time:** Each time when we launch the emulator we add a flag.

  You can pass in additional parameters to the emulator by setting
  `TURN` environment variable in the container you wish to launch.
  The environment variable should contain the command you wish to execute to
  obtain the turn configuration, for example you could use curl to obtain a
  a snippet:

  ```sh
    docker run  \
     -e ADBKEY="$(cat ~/.android/adbkey)" \
     -e TURN="curl -s -X POST https://networktraversal.googleapis.com/v1alpha/iceconfig?key=mykey" \
     --device /dev/kvm  \
     --publish 8554:8554/tcp \
     --publish 5555:5555/tcp ${CONTAINER_ID}
  ```

- **During build time:** Embed the additional flag in the container itself. Everyone who launches your created container will use this flag unless it is manually overriden!

  You can create the docker container with the `--extra` flag to pass in the turn configuration. For example to use a static configuration:

  ```sh
  emu-docker create canary \
         "R" \
         --extra  \
         '-turncfg '\\\''printf {\"iceServers\":[{\"urls\":\"turn:\",\"username\":\"webrtc\",\"credential\":\"turnpassword\"}]}'\\\'' '
  ```

  Note the `'\\\''` to escape a single `'` and `\"` to escape `"`, as we want pass the following flag to emulator:

  ```sh
    -turncfg 'printf {"iceServers":[{"urls":"turn:","username":"webrtc","credential":"turnpassword"}]}'
  ```

  when launching the emulator.
