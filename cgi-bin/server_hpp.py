#!/usr/local/adyen/python3/bin/python3

# imports
import sys			## format printing of HTTP response
import cgi, cgitb	## handle server requests
import json			## methods for JSON objects

# merchant signature
import base64, binascii				## encoding / decoding
import hmac, hashlib				## cryptography libraries
from collections import OrderedDict	## for sorting keys

# URL / request helpers
import datetime     ## for sessionvalidity field
import webbrowser   ## to redirect user to HPP
from urllib.parse import urlencode	## format data to send to Adyen

# enable debugging cgi errors from the browser
cgitb.enable()

# parse payment data from URL params
data = {}
form = cgi.FieldStorage()
for key in form.keys():
	data[key] = form.getvalue(key)

# server side fields
data["sessionValidity"] = datetime.datetime.now().isoformat().split(".")[0] + "-11:00"
data["shipBeforeData"] = datetime.datetime.now().isoformat().split(".")[0] + "-11:00"
data["brandCode"] = "mc"

# generate merchant signature

# HMAC key
KEY = "BE1C271E9CD9D2F6611D2C7064FE9EE314DA58539195E92BF5AC706209A514DB"

# sort data alphabetically by keys
sorted_data = OrderedDict(sorted(data.items(), key=lambda t: t[0]))

# escape special characters
escaped_data = OrderedDict(map(lambda t: (t[0], t[1].replace('\\', '\\\\').replace(':', '\\:')), sorted_data.items()))

# join all keys followed by all values, separated by colons
signing_string = ":".join(escaped_data.keys()) + ":" + ":".join(escaped_data.values())

# convert to hex
binary_hmac_key = binascii.a2b_hex(KEY)

# calculate merchant sig
binary_hmac = hmac.new(binary_hmac_key, signing_string.encode("utf8"), hashlib.sha256)

# base64 encode signature
signature = base64.b64encode(binary_hmac.digest())

# generate HMAC signature
data["merchantSig"] = signature

# respond with headers
sys.stdout.write("Content-type:application/json\r\n\r\n")

# send data for debugging
print(data)

# redirect to HPP page in new window
url = "https://test.adyen.com/hpp/skipDetails.shtml"
webbrowser.open_new(url + "?" + urlencode(data))