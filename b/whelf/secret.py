#!/usr/bin/env python
from Crypto.Cipher import AES
import base64
secret = base64.b64decode("lu5Hj2srcOy7wQl0nrTJ0Q==")
cipher = AES.new(secret)
