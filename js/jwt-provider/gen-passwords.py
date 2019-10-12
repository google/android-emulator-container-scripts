# Lint as: python3
"""A simple tool to generate a password file and JWKS secrets."""

import json
import binascii

from absl import app, flags, logging
from werkzeug.security import check_password_hash, generate_password_hash
from jwcrypto import jwk
import getpass

FLAGS = flags.FLAGS

flags.DEFINE_list("pairs", [getpass.getuser() + "@localhost", "hello"], "List of user name password pairs. user1,passwd1,user2,passwd2,...")
flags.DEFINE_string("passwords", "passwd", "File with json dictionary of users -> password hash")
flags.DEFINE_string("jwks", "jwt_secrets", "File name with generated  JWKS secrets.")

flags.register_validator(
    "pairs", lambda value: len(value) % 2 == 0, message="--pairs must have an even number of user,password pairs"
)


def pairwise(iterable):
    "s -> (s0, s1), (s2, s3), (s4, s5), ..."
    a = iter(iterable)
    return zip(a, a)


def main(argv):
    if len(argv) > 1:
        raise app.UsageError("Too many command-line arguments.")

    # Create salted passwords
    unsalted = pairwise(FLAGS.pairs)
    salted = {}
    for pair in unsalted:
        logging.info("%s : %s", pair[0], pair[1])
        salted[pair[0]] = generate_password_hash(pair[1])

    # And write them to a file
    with open(FLAGS.passwords, "w") as f:
        f.write(json.dumps(salted))

    # Create the jwks secrets and export them
    keys = jwk.JWK.generate(kty="RSA", size=2048)

    # Python 2 does signed crc32, unlike Python 3
    kid = hex(binascii.crc32(keys.export_public().encode('utf-8')) & 0xFFFFFFFF)

    public = json.loads(keys.export_public())
    private = json.loads(keys.export_private())
    public["kid"] = kid
    private["kid"] = kid
    public_jwks = {"keys": [public]}
    private_jwks = {"keys": [private]}

    with open(FLAGS.jwks + '_pub.jwks', 'w') as f:
        f.write(json.dumps(public_jwks, indent=2))

    with open(FLAGS.jwks + '_priv.jwks', 'w') as f:
        f.write(json.dumps(private_jwks, indent=2))


if __name__ == "__main__":
    app.run(main)
