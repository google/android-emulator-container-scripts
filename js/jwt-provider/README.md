Sample JWT service
==================
This is a sample [JWT](https://en.wikipedia.org/wiki/JSON_Web_Token) token service. 
The general idea is that a user obtains a token from this service and presents this 
token to get access to the emulator. In this sample service you authenticate with this
service using [Basic Auth](https://en.wikipedia.org/wiki/Basic_access_authentication)
to obtain a token that can be used for up to two hours.

The envoy web proxy will validate this token and give you access to the emulator. 

# Deployment

This service contains two scripts of interest:

- `gen-passwords.py`: Responsible for creating a salted password file and a public and private JWKS store. 
                      The public JWKS is to be used by the envoy proxy to verfify that the tokens are properly
                      signed.

- `jwt-provider.py`: A simple flask rest server that hands out JWT tokens for everyone who can authenticate using
                     Basic Auth. 


If you are planning to deploy the emulator in a publicly accessible environment you will want to replace this 
component with your own server that can hand out tokens.


