#!/usr/local/adyen/python3/bin/python3

# imports
import sys			## format printing of HTTP response
import cgi			## handle server requests
import json			## methods for JSON objects
import base64		## for creating auth string

from urllib.request import Request, urlopen		## for sending requests to Adyen

# hardcoded values
LOCAL_ADDRESS = "http://localhost:8080"
RETURN_URL = "http://localhost:8080/cgi-bin/server_test.py"
CHECKOUT_API_KEY = "AQEyhmfxLIrIaBdEw0m/n3Q5qf3VaY9UCJ1+XWZe9W27jmlZilETQsVk1ULvYgY9gREbDhYQwV1bDb7kfNy1WIxIIkxgBw==-CekguSzLVE/iCTVQQWGILQK0x8Lo88FEQ/VHTZuAoP0=-dqZewkA79CPfNISf"

def setup(data):

	# URL and headers
	url = "https://checkout-test.adyen.com/services/PaymentSetupAndVerification/setup"
	header_object = {
		"Content-Type": "application/json",
		"x-api-key": CHECKOUT_API_KEY
	}

	# static fields
	data["html"] = "true"
	data["origin"] = LOCAL_ADDRESS
	data["returnUrl"] = RETURN_URL
	data["reference"] = "Integrations overview - checkout"

	# shopper information (should be on the front-end)
	data["shopperName"] = {}
	data["shopperName"]["firstName"] = "Simon"
	data["shopperName"]["lastName"] = "Hopper"
	data["shopperName"]["gender"] = "MALE"

	# address info to be passed through to Paypal / etc
	data["configuration"] = {}
	data["configuration"]["cardHolderNameRequired"] = "false"
	data["configuration"]["avs"] = {}
	data["configuration"]["avs"]["enabled"] = "automatic"
	data["configuration"]["avs"]["addressEditable"] = "true"

	data["billingAddress"] = {}
	data["billingAddress"]["city"] = "Springfield"
	data["billingAddress"]["country"] = "US"
	data["billingAddress"]["houseNumberOrName"] = "1234"
	data["billingAddress"]["postalCode"] = "74629"
	data["billingAddress"]["stateOrProvince"] = "OR"
	data["billingAddress"]["street"] = "Main"

	# recurring
	data["enableRecurring"] = "true"
	data["enableOneClick"] = "true"

	# paypal
	data["shopperEmail"] = "test.shopper@gmail.com"

	# indent amount data
	data["amount"] = {
		"value": data["value"],
		"currency": data["currency"]
	}
	del data["value"]
	del data["currency"]

	# get and return response
	request = Request(url, json.dumps(data).encode("UTF8"), header_object)
	response = urlopen(request).read()

	# respond to browser
	sys.stdout.write("Content-type:application/json\r\n\r\n")
	print(response.decode("UTF8"))

# javascript checkout SDK
def verify(data):

	# URL and headers
	url = "https://checkout-test.adyen.com/services/PaymentSetupAndVerification/verify"
	header_object = {
		"Content-Type": "application/json",
		"x-api-key": CHECKOUT_API_KEY
	}

	# get and return response
	request = Request(url, json.dumps(data).encode("UTF8"), header_object)
	response = urlopen(request).read()

	# respond to browser
	sys.stdout.write("Content-type:application/json\r\n\r\n")
	print(response.decode("UTF8"))



# route requests dynamically
#
# in a production environment you would
# use a framework like Flask or Django

# parse payment data from URL params 
form = cgi.FieldStorage()
data = {}

# pull data from http request into data object
for key in form.keys():
	data[key] = form.getvalue(key)

# map endpoint values to functions
router = {
	"setup": setup,
	"verify": verify
}

# send data to appropriate function
# and remove from data object
endpoint = data["endpoint"]
del data["endpoint"]
router[endpoint](data)

