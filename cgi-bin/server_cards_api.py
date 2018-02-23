#!/usr/local/adyen/python3/bin/python3

# imports
import sys			## format printing of HTTP response
import cgi, cgitb	## handle server requests
import json			## methods for JSON objects
import base64		## for creating auth string

from urllib.request import Request, urlopen		## for sending requests to Adyen

# enable debugging cgi errors from the browser
cgitb.enable()

# user credentials
WS_USER = "ws_306326@Company.AdyenTechSupport"
WS_PASS = "7UuQQEmR=2Qq9ByCt4<3r2zq^"

# generate headers for response
# USER:PASS -> base64 encode
basic_auth_string = "{}:{}".format(WS_USER, WS_PASS)
basic_auth_string = base64.b64encode(basic_auth_string.encode("utf8")).decode("utf8")

header_object = {
	"Content-type": "application/json",
	"Authorization": "Basic {}".format(basic_auth_string)
}

# parse payment data from URL params 
form = cgi.FieldStorage()

# create object to send to Adyen
data = {}

# transfer data from form object to our request
data["reference"] = form.getvalue("reference")
data["merchantAccount"] = form.getvalue("merchantAccount")

# indent card and amount data to conform to Adyen specs
data["card"] = {
	"number": form.getvalue("number"),
	"expiryMonth": form.getvalue("expiryMonth"),
	"expiryYear": form.getvalue("expiryYear"),
	"cvc": form.getvalue("cvc"),
	"holderName": form.getvalue("holderName")
}

# indent amount data
data["amount"] = {
	"value": form.getvalue("value"),
	"currency": form.getvalue("currency")
}

# create request to server
url = "https://pal-test.adyen.com/pal/servlet/Payment/authorise"

# create request object
request = Request(url, json.dumps(data).encode("UTF8"), header_object)

# sends data to server
response = urlopen(request).read()

# respond with headers
sys.stdout.write("Content-type:application/json\r\n\r\n")

# send data for debugging
print(form)
print(data)
print("-----------------")
print(response)








