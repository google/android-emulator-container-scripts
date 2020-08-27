# Lint as: python3
"""A basic example of a service that can hand out temporary access to a turn server.

It follows the rest api for access to turn services:

https://tools.ietf.org/html/draft-uberti-rtcweb-turn-rest-00
"""

import base64
import hmac
import hashlib
import time

from absl import app, flags
from flask import Flask, request, abort

FLAGS = flags.FLAGS
flags.DEFINE_string("static_auth_secret", "supersecret", "The shared secret with the turn server.")
flags.DEFINE_string("api_key", "supersafe", "The api key the emulator will present to retrieve turn configuration.")
flags.DEFINE_integer("port", 8080, "The port where this service will run")

api = Flask(__name__)


@api.route("/turn/<iceserver>", methods=["GET"])
def get_turn_cfg(iceserver):
    """Generates a turn configuration that can be used by the emulator.
       The turn configuration is valid for 1 hour.

       See: https://tools.ietf.org/html/draft-uberti-rtcweb-turn-rest-00

       Your turn server should be configured to use the same static auth secret as
       the turn server

       For example:

       turnserver -n -v --log-file=stdout --static-auth-secret=supersecret \
            -r localhost -use-auth-secret

       python turn.py --static_auth_secret supersecret

       Args:
        iceserver: The turn server under your control that uses the
                   shared secret.
      """
    if request.args.get("apiKey") != FLAGS.api_key:
        abort(403, description="Invalid api key")

    epoch = int(time.time()) + 3600  # You get an hour.
    userid = "{}:{}".format(epoch, "someone")  # Username doesn't matter.
    key = bytes(FLAGS.static_auth_secret, "UTF-8")  # Shared secret with coturn config
    mac = hmac.digest(key, bytes(userid, "UTF-8"), hashlib.sha1)
    credential = base64.b64encode(mac).decode()
    return {"iceServers": [{"urls": ["turn:{}".format(iceserver)], "username": userid, "credential": credential}]}


def main(argv):
    if len(argv) > 1:
        raise app.UsageError("Too many command-line arguments.")
    api.run(host="0.0.0.0", port=FLAGS.port)


if __name__ == "__main__":
    app.run(main)
