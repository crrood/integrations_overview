# Integration overview notes

## Session 1 - Hello world and raw card transactions:

### Check openSSL version
Make sure that you're able to send TLSv1.2 requests

`/usr/local/adyen/python3/bin/python3 -c "import ssl; print(ssl.OPENSSL_VERSION)"`

The result should be greater than 1, for instance `OpenSSL 1.0.2n  7 Dec 2017`
<br><br>

### Create basic form
Send dummy data to the server to echo back to the client

`test.html`
```HTML
<form action="cgi-bin/server_test.py" method="POST">
	<input type="text" name="testValue" value="Hello world!"/>
	<input type="submit"/>
</form>
```
<br>

### Create basic backend
Parses data into an object we can use in python, and displays it back to the browser

`./cgi-bin/server_test.py`
```Python
#!/usr/local/adyen/python3/bin/python3

# imports
import sys          ## format printing of HTTP response
import cgi, cgitb   ## handle server requests

# enable debugging cgi errors from the browser
cgitb.enable()

# parse payment data from URL params 
form = cgi.FieldStorage()

# respond with headers
sys.stdout.write("Content-type:text/plain\r\n")
sys.stdout.write("\r\n")

# send data for debugging
print(form)
print(form.getvalue("testValue"))
```
<br>

### Start testing server
We're going to use the built-in python 2.7 CGI server

`python -m CGIHTTPServer 8080`

If you want to use python 3.* instead:

`python -m http.server --cgi 8080`

Point your browser to localhost:8080/test.html, and submit the form.  You should see the form data displayed in the browser as a python FieldStorage object, plus the specific field we chose to display.

If you get a permission error, type `chmod +x cgi-bin/server_test.py`
<br><br>

### Create form to collect card data from user
Same as test.html, but gets all the information needed to submit a test card transaction

`cardsAPI.html`
```HTML
<form action="cgi-bin/server_cards_api.py" method="POST">
	Number: <input type="text" name="number" value="4111111111111111"/><br>
	Expiry Month: <input type="text" name="expiryMonth" value="8"/><br>
	Expiry Year: <input type="text" name="expiryYear" value="2018"/><br>
	CVC: <input type="text" name="cvc" value="737"/><br>
	Holder Name: <input type="text" name="holderName" value="John Smith"/><br>
	Value: <input type="text" name="value" value="1500"/><br>
	Currency: <input type="text" name="currency" value="EUR"/><br>
	Reference: <input type="text" name="reference" value="Test payment"/><br>
	Merchant Account: <input type="text" name="merchantAccount" value="ColinRood"/><br>
	<input type="submit"/>
</form>
```
<br>

### Process card data on the backend
Format request to match Adyen specs, and send to the PAL

This is what we want our request to look like:
```JSON
{
  "card": {
    "number": "4111111111111111",
    "expiryMonth": "8",
    "expiryYear": "2018",
    "cvc": "737",
    "holderName": "John Smith"
  },
  "amount": {
    "value": 1500,
    "currency": "EUR"
  },
  "reference": "payment-2017-5-30-16",
  "merchantAccount": "YOUR_MERCHANT_ACCOUNT"
}
```

Here's the code to make it happen:

`cgi-bin/server_cards_api.py`
```Python
#!/usr/local/adyen/python3/bin/python3

# imports
import sys          ## format printing of HTTP response
import cgi, cgitb   ## handle server requests
import json         ## methods for JSON objects
import base64       ## for creating auth string

from urllib.request import Request, urlopen		## for sending requests to Adyen

# enable debugging cgi errors from the browser
cgitb.enable()

# user credentials
WS_USER = "" ## enter your webservice username here
WS_PASS = "" ## enter your webservice password here

# generate headers for response
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
response = urlopen(request).read()

# respond with headers
sys.stdout.write("Content-type:application/json\r\n\r\n")

# send data for debugging
print(form)
print(data)
print("-----------------")
print(response)
```

## Session 2 - HPP and CSE

### Create form for HPP /setup request
Same structure as cards, but with different data:

`HPP.html`
```HTML
<html>

<body>
<form id="infoForm" class="clientForm" action="cgi-bin/server_hpp.py">
	AllowedMethods: <input type="text" id="allowedMethods" name="allowedMethods" value=""/><br>
	Amount: <input type="text" id="paymentAmount" name="paymentAmount" value="199"/><br>
	MerchantReference: <input type="text" id="merchantReference" name="merchantReference" value="HPP payment"/><br>
	Currency: <input type="text" id="currencyCode" name="currencyCode" value="USD"/><br>
	CountryCode: <input type="text" id="countryCode" name="countryCode" value="US"/><br>
	ShopperLocale: <input type="text" id="shopperLocale" name="shopperLocale" value="en_GB"/><br>
	ShopperReference: <input type="text" id="shopperReference" name="shopperReference" value="HPP shopper 1"/><br>
	<!-- CHANGE TO YOUR TEST MERCHANT ACCOUNT -->
	MerchantAccount: <input type="text" id="merchantAccount" name="merchantAccount" value="ColinRood"/><br>
	<!-- ENTER YOUR SKINCODE BELOW -->
	SkinCode: <input type="text" id="skinCode" name="skinCode" value="rKJeo2Mf"/><br>
	resURL: <input type="text" id="resURL" name="resURL" value="http://localhost:8080/cgi-bin/server_test.py"/><br>
	<input type="submit" class="submitBtn" id="checkoutBtn" value="Checkout"/>
</form>
</body>

</html>
```

### Create backend to send data to Adyen
We're going to take the same basic structure that we used for cards, and add signature calculation and a browser redirect.

`cgi-bin/server_hpp.py`
```Python
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
url = "https://test.adyen.com/hpp/pay.shtml"
webbrowser.open_new(url + "?" + urlencode(data))
```

### Result page (optional)
So that we can mimick the shopper being sent back to the Merchant's website, we'll create an endpoint which will display the data sent back from Adyen on a successful payment.

Since we already did this as part of our Hello World program, we'll re-use the same file:

`cgi-bin/server_test.py`
```Python
#!/usr/local/adyen/python3/bin/python3

# imports
import sys			## format printing of HTTP response
import cgi, cgitb	## handle server requests

# enable debugging cgi errors from the browser
cgitb.enable()

# parse payment data from URL params 
form = cgi.FieldStorage()

# respond with headers
sys.stdout.write("Content-type:text/plain\r\n")
sys.stdout.write("\r\n")

# send data for debugging
print(form)
# print(form.getvalue("testValue"))  ## <-- COMMENT OUT THIS LINE
```

Note that you have to remove / comment out `print(form.getvalue("testValue"))`.  Otherwise python will try to find a "testValue" field in the response data, and will crash when one doesn't exist.