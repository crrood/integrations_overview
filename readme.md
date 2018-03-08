# Integration overview notes

## Section 1 - Hello world and raw card transactions:

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
<br><br>
## Section 2 - HPP

### Get the project from Github
Lets get all the code at once instead of copying piece by piece.  Open a terminal and navigate to where you want to put your project, then run:
```bash
git clone https://github.com/crrood/integrations_overview.git
cd integrations_overview
./start_server
```
This will create the project, update permissions, and start the server.
<br><br>

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
<br>

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
import datetime     ## for Sectionvalidity field
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
data["SectionValidity"] = datetime.datetime.now().isoformat().split(".")[0] + "-11:00"
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
<br>

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
<br><br>
## Section 3 - CSE

### Create HTML forms
Because the encryption library runs on the front-end, the web side of CSE is much more complicated than API or HPP.  First we'll set up two separate forms for the payment and card details:

`CSE.HTML`
```HTML
<body>

	<h3>Payment info</h3>
	<form id="paymentForm">
		Value: <input type="text" name="value" value="1500"/><br>
		Currency: <input type="text" name="currency" value="USD"/><br>
		Reference: <input type="text" name="reference" value="CSE Payment"/><br>
		<!-- REPLACE THIS WITH YOUR OWN TEST MERCHANT ACCOUNT -->
		MerchantAccount: <input type="text" name="merchantAccount" value="ColinRood"/><br>
	</form>

	<h3>Card info</h3>
	<form  id="adyen-encrypted-form">
		<div id="cardType" ></div><br>
		Number: <input type="text" size="20" data-encrypted-name="number" value="4111111111111111"/><br>
		Name: <input type="text" size="20" data-encrypted-name="holderName" value="Test Person"/><br>
		Expiry Month: <input type="text" size="2" data-encrypted-name="expiryMonth" value="08"/><br>
		Expiry Year: <input type="text" size="4" data-encrypted-name="expiryYear" value="2018"/><br>
		CVC: <input type="text" size="4" data-encrypted-name="cvc" value="737"/><br>
		<input type="hidden" id="adyen-encrypted-form-expiry-generationtime" value="" data-encrypted-name="generationtime"/>
		<input type="submit"  value="Pay"/>
	</form>
	<button id="logBtn">Log form data</button>

</body>
```
<br>

### Import Adyen encryption libraries
Download the adyen encryption library from https://raw.githubusercontent.com/Adyen/adyen-cse-web/master/js/adyen.encrypt.min.js and save it to `scripts/adyen.encrypt.min.js`.

Then add an import tag to your HTML at the end of the body section:

`CSE.HTML`
```HTML
<!-- Make sure the library is *NOT* loaded in the "head" of the HTML document -->
<script type="text/javascript" src="scripts/adyen.encrypt.min.js"></script>
```
<br>

### Add javascript to activate encryption
For the sake of readability, we'll put the javascript directly into the HTML file:

`CSE.HTML`
```javascript
// based heavily on:
// https://github.com/Adyen/adyen-cse-web/blob/master/adyen.encrypt.simple.html

// set up options and initialize encrypted form object
// run on page load
function initCardsCheckout() {

	// Generate current time client-side (unsafe)
	var isoDate = new Date().toISOString();
	isoDate = isoDate.substring(0, isoDate.length - 1) + "-8:00";
	document.getElementById('adyen-encrypted-form-expiry-generationtime').value = isoDate;

	// The form element to encrypt.
	var form = document.getElementById('adyen-encrypted-form');

	// See https://github.com/Adyen/CSE-JS/blob/master/Options.md for details on the options to use.
	var options = {
		"enableValidations": false,
	};

	// Method to send form to server
	options.onsubmit = onSubmit;

	// Assign pointer to card type indicator in DOM
	// options.cardTypeElement = document.getElementById('cardType');

	// Set key value from webservice user in Customer Area
	var key = "10001|DAAA84F903B74D76E2E452201F49998FAF18743AF5BBE880E169752F3C60B8C5C601E99CBF66C4DAE57B818ECA837FD0A53A70FFC7515796E0CB4D4A07B15A1D0496B3E2D41A8099A25E055E5224E15AF203F8EDFBDA9FCCF6A5793AA3C620CB62D81F9103BF5EF362531D8742B84B597F46D2B29ABFE680DB09F1AE6B9D4ED3CBEDA22E3CC4D388BAC76A39116E0CA787483419B941F24FFD9EB2DC158EA20CA5A84D1DB1E3B5FEE2B8AB5512EAF7DE572366B10D5C57C09F3002CF0FD0AE557887C4078DE00EB48CDD6763BD976C969D91200C5DB11B2C3B002B4C31EC5BBFB27B00791813757C21D631DCC1E9B74610BCA05F5CFA4DE0662C0F561CF616BB"

	// Create the form object and bind encryption options to the form.
	encryptedForm = adyen.encrypt.createEncryptedForm(form, key, options);

	// Activate the card type indicator
	// encryptedForm.addCardTypeDetection(options.cardTypeElement)
}

function onSubmit(e) {
	// prevent the default redirect
	e.preventDefault();

	// build URL encoded query string to send to server
	var params = "?endpoint=CSE&"

	// get value and currency for transaction
	var paymentForm = document.getElementById("paymentForm");
	var element;
	for (var i = 0; i < paymentForm.elements.length; i++) {
		element = paymentForm.elements[i];
		params = params + element.name + "=" + element.value + "&";
	}

	// The form element to encrypt
	var form = document.getElementById("adyen-encrypted-form");

	// get encrypted card data from form element
	params = params + "encryptedData=" + encodeURIComponent(form.elements["adyen-encrypted-data"].value) + "&";

	// redirect to server
	window.location = "./cgi-bin/server_cse.py" + params;
}

initCardsCheckout();
```

Let's make sure that everything is working on the front-end by changing the last line to `window.location = "./cgi-bin/server_test.py" + params;` and submitting the form.  You should see something like this:

```
FieldStorage(None, None, [MiniFieldStorage('endpoint', 'CSE'), MiniFieldStorage('value', '1500'), MiniFieldStorage('currency', 'USD'), MiniFieldStorage('reference', 'CSE Payment'), MiniFieldStorage('merchantAccount', 'ColinRood'), MiniFieldStorage('encryptedData', 'adyenjs_0_1_21$jJYbNgVKnLgip1HyBm6ueQwT7YsEAX1nu6ARhT2FOVRzb1UrmI2jEZ3h2Hw60PhyaVlxm3tomcDt9I9U9CdsP8r8T8pqkYjstIzMyyG7pBgX3CJG0lBaPXXD6OZbzsSi7rg7 qd/062VAvfAf1CY0GX4JhS3Z6kVILSjV0ygZAGxIU/1dtONjLHN9tPtjWK7gixL9BSCMxnS6BU uXt1J8dn6rptcrUAhZm2mt2IP24IvJ6M6q/mGAlNzfE4XTv/c4IqVAqABCgYQSyaRtpZ5evXm44/27 eSkq0hH I1rnCh6Ul76CwAR9XGesIYq8lHJIj29ej7/Gkr/c4OyxfbQ==$HoDVfZ8yFplG k/KeHZiS8bk1g7ROcYqUnSiDIaWKvKJnDSkoo96IPzV5Pzgm5RaU9dR3YySIInvRA1rHDnVi1mkr1 F1  BFrYNsswcQOk9rw3Hvf/yce8bw8yxinXuRatfP/LpTfUQVsNIkW2dYMrjymTpkzEwbRsewi6bFbw659I 2i4FT1vJAAdGDn2NNCXMIbDXdqhA2kTWzWjcQhPic3jhszuQ zB3QvZpupNRgTkMAnUHJN/V3YsJy74qoydZJol7rcLqftRLVs/w85Hf Al3Rc0RSKPABV6ECs0/apNvHhU1WB3BZZ36SoIWynGYZbAK3wDOvFGl2xAYpRjkEjZ2YiKIiWLFmeD ouREaOHzm pKL4VyGMHFId/Tux 3rxWSUHC6T65CNDF0IX9skksmhfEOofGduATCtMA3Dt1c3AFTt3KFbiyrAzlugLuTqfa07iKdDLPQW8DuwlZ SVv3l7yn/umag6HOd TuckPMJ69KAP0tcvDfusSk8snhuRGJZFgYNkkPuVEIAiIOcWs/rScdeYj4ZnUS5RsR1LchkuBigbj8bH3Jotjp2UggOI2tMmzOEbI9/y NPlviIYS0y81w/AZQ22yn S0oDXSGQo5zmsZ2pNrw8R /a7tqlHTFo11oWA3nnarHX6 jKHHT/9o=')])
```
<br>

### Implement the CSE server
The hard part is done already - now we just need to send the data to the Adyen server:

`cgi-bin/server_cse.py`
```Python
#!/usr/local/adyen/python3/bin/python3

# imports
import sys			## format printing of HTTP response
import cgi, cgitb	## handle server requests
import json			## methods for JSON objects
import base64		## for creating auth string

from urllib.request import Request, urlopen		## for sending requests to Adyen

# import os
# from urllib.parse import parse_qs

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

# indent amount data
data["amount"] = {
	"value": form.getvalue("value"),
	"currency": form.getvalue("currency")
}

# move encrypted card data into additionalData container
data["additionalData"] = {
	# the cgi url decoder mistakes "+"" for " " and must be corrected
	"card.encrypted.json": form.getvalue("encryptedData").replace(" ", "+")
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
print(data)
print("-----------------")
print(response)
```
<br>

### Fire it up!
Modify the redirect in CSE.html to server_cse.py, and submit the form to the server.  You should see the data from your call, and a successful response from Adyen:
```JSON
{'merchantAccount': 'ColinRood', 'additionalData': {'card.encrypted.json': 'adyenjs_0_1_21$1w0e8USxzM4n66zqbC86S+L0nziRyWDsHePKsj+8dwz7zKqSyRdo0U4GI+5964sgECf+Cw+WFBPeixJY+nzO77rJSEVqz1GY/jlCs3tjd36tuKpjPiSJ1AMsVIoYzKJdtOjyRL2yF7Yo/lXcflPGY/2eoFLTuq3eKn1QgABWwVJJLG9Y7x7263aM02sLY7JSnjN6/RKxzHCHksYHTNYs4f5leqBWooH16Tw59KoOgSztAwMC4Oqx2BhgUeZ3ue+sQI8BuL22hCi2LPoWmrA6luTiXRYW4S8qKpgaQqhOjUmO8lrfLCd8vnj3cJwL5IigoC6d+eOYZRt5nm3tP1A9ug==$O2ovqLU9BfAD5IYeigw3MmqKMCTzXh6cki4E9rYh03UZx34ztYpwsdDAEekYQNzlAn2adPfyV99wLCa/XAda8CySUqpTHkv+eKvwQDD7GUTxn6DCPjvnX84RkhYSAOmI0k/KrFuHyMRyCUeEX1dFBQ2Q0XRT8llT4Cb7SICY+swINpOxjU6eyogiEJDZWhAOxGhRDA0KYHHhCuOhEA261hEqhOUsmDaqAUcx9GSof5Z74vBwY2YkdtxGUhl4Jqbu5/mYRXAnwITaZc79lGWAiA4RzyPo0OeO6g2d9OUeOzKZsUUIA5Zvbno7rYEWY9phg0QptdHo3YW3XcAVQMjfQXtTElPUzrIeqnTbuYtfcGpMcTUgJiaRsbp49rUvRA3RA4YJmkPZUrqXBpB7p34aSKyiVWIN9WPQj4fRevQ6b8J3bCKnvKJFlTkP9TkBBZfIx21NS8VI6dOlU9GHSnNtNiiAExAtzWV4JPyiciJtLGsxLjARpOQkPcKsQ6tw8EZ+RL4BqDnfBLRMn8MyTrLuoJZn8YGUmYcVRgQCvZd8xePJDTNBW0z5ZUYdUaLL9KA00Yki0HRzncvsEUp7EdzDYoibytIX386wU8i/x1KGhNiI2o6JcmUJhiiXRgbAaIzxAEMg++SB9ea1Q0gtHeLqpBUVwjbTp0U='}, 'reference': 'CSE Payment', 'amount': {'value': '1500', 'currency': 'USD'}}
-----------------
b'{"additionalData":{"riskProfile":"ColinRood","cardBin":"411111","aliasType":"Default","alias":"H167852639363479","cardPaymentMethod":"visa","cardIssuingCountry":"NL"},"pspReference":"8835199231328456","resultCode":"Authorised","authCode":"96317"}'
```

## Section 4 - Checkout Front-end
I'm going to add some more advanced features to this integration, including separate scripts, AJAX, and some basic CSS.  If you've never seen any of it before it's more than you can probably learn in an hour, so I'd encourage you to go back and play with some of the logic and settings to see what they do.

### SDK Overview
Besides the setup form, there are two main components of the Checkout SDK:

- The SDK itself, loaded via a script tag:
```HTML
<script type="text/javascript" src="https://checkoutshopper-test.adyen.com/checkoutshopper/assets/js/sdk/checkoutSDK.1.2.0.min.js"></script>
```
- A div element which the checkout attaches itself to via javascript:
```HTML
<div class="checkout" id="checkout">
```
```javascript
var checkout = chckt.checkout(data, '.checkout', sdkConfigObj);
```

### AJAX
Because the Checkout SDK is loaded directly into the client page without a redirect, we also need to be able to send server calls without changing the page address.  This is called AJAX (Asynchronous Javascript And XML), and forms the basis of much of the modern web.

There is an excellent library called JQuery which is used by most websites and handles AJAX very elegantly, but for learning purposes we're going to use plain javascript:
```javascript
// Send request to server
function AJAXPost(path, headers, method, callback) {

	// Initialize a request object
	var request = new XMLHttpRequest();
	request.open(method || "POST", path, true);

	// Tell the browser what to do when we get a response
	request.onreadystatechange = callback;

	// Iterate through headers and add to request object
	for (var key in headers) {
		request.setRequestHeader(key, headers[key]);
	}

	// Send request to server
	request.send({});
};
```

### Complete HTML
Here's the full HTML we'll be using:

`checkout.html`
```HTML
<html>

<head>
	<script type="text/javascript" src="https://checkoutshopper-test.adyen.com/checkoutshopper/assets/js/sdk/checkoutSDK.1.2.0.min.js"></script>
	<script type="text/javascript" src="scripts/checkout.js"></script>
</head>

<body>
	<h4>Checkout should appear below:</h4>
	<div class="checkout" id="checkout">
		<form id="infoForm" action="http://localhost:8000/cgi-bin/checkout_requester.py">
			<div>Amount: <input type="text" id="value" name="value" value="199"/><br></div>
			<div>Currency: <input type="text" id="currency" name="currency" value="USD"/><br></div>
			<div>CountryCode: <input type="text" id="countryCode" name="countryCode" value="US"/><br></div>
			<div>ShopperLocale: <input type="text" id="shopperLocale" name="shopperLocale" value="en_GB"/><br></div>
			<div>ShopperReference: <input type="text" id="shopperReference" name="shopperReference" value="localhostCheckout1"/><br></div>
			<div>Channel: <input type="text" id="channel" name="channel" value="Web"/><br></div>
			<div>MerchantAccount: <input type="text" id="merchantAccount" name="merchantAccount" value="ColinRood"/><br></div>
			<input type="button" id="checkoutBtn" value="Checkout"/>
		</form>
	</div>
	<hr>
	<div id="verifyContainer" style="display: none;">
		<input type="button" id="verifyBtn" value="Verify Payment"/>
		<div id="verifyResult"></div>
	</div>
</body>

</html>

<script>

initPage();

</script>
```

### Configure the SDK
The Checkout Web SDK is highly configurable by passing JSON objects during the setup process.  The full list of options is in our docs at https://docs.adyen.com/developers/checkout/web-sdk/customization/

Here are the settings we're going to use:
```Javascript
// Custom text
var translationObject = {
    payButton: {
        "en-US": "Subscribe",
        "nl-NL": "Meer opties"
    }
};

// Customer styling for card fields
var styleObject = {
    base: {
        color: '#00F',
        fontSize: '14px',
        lineHeight: '14px',
        fontSmoothing: 'antialiased'
    },
    error: {
        color: 'red'
    },
    placeholder: {
        color: '#d8d8d8'
    },
    validated: {
        color: 'green'
    }
};

// Styling for larger Checkout object
var sdkConfigObj = {
	base: {
		fontSize: '16px',
		background: "#68FFC1",
		outline: "2px black",
		color: "blue",
	},
	paymentMethods: {
		card: {
			sfStyles: styleObject
		}
	},
	context: "test",
	translations: translationObject
};
```

### Prepare the /setup server call
Remember callbacks?  Here's another one:

```javascript
// Add eventListener to Checkout button
function initPage() {

	// The second parameter of addEventListener is the callback to use when the event fires
	document.getElementById("checkoutBtn").addEventListener("click", openCheckout);
}

// Collect setup data to send to server
function openCheckout() {
	var inputParams = document.querySelectorAll("input[type=text]");

	// Get request details from html form
	// You could 
	var formString = "";
	for (var param of inputParams) {
		formString = formString + param.name + "=" + param.value + "&";
	}
	formString = formString + "endpoint=setup";

	// Set parameters for request to server
	var url = "./cgi-bin/server_checkout.py";
	var headers = { "Content-Type": "application/x-www-form-urlencoded" };
	var method = "POST";

	// calls async javascript function to send to server
	AJAXPost(encodeURI(url + "?" + formString), headers, method, setupCallback);
}
```

And here's the callback which is executed once the response comes back from Adyen:
```javascript
// Handle response from setup call
setupCallback = function() {

	// Only execute this function if the response is complete
	if (this.readyState == 4) {
		console.log(this);

		try {
			// Parse response to JSON 
			var data = JSON.parse(this.responseText);

			// Initialize checkout
			var checkout = chckt.checkout(data, '.checkout', sdkConfigObj);

			// Handle response from initiate call
			chckt.hooks.beforeComplete = function(pNode, pHookData, pData){
				setupVerify(pHookData);
				console.log(JSON.stringify(pData));
			}

			// Debug hooks
			chckt.hooks.beforeRedirect = function() {
				console.log("beforeRedirect");
			}
			chckt.hooks.beforePendingRedirect = function(selectedPMNode/*HTML Node*/, extraData/*Object*/) {
				console.log("beforePendingRedirect");
				selectedPMNode.style.opacity = '0.2';
				extraData.actionButton.style.opacity = '0.2';
				return false;
			};
		}
		catch (e) {
			console.log("error:");
			console.log(e);
			document.getElementById("checkout").innerHTML = this.responseText;
		}
	}
};
```

### Verify call

We're also going to add an element to view the verify result which we'll activate via javascript once the SDK tells us the payment is complete:

`checkout.html`
```HTML
<div id="verifyContainer" style="display: none;">
	<input type="button" id="verifyBtn" value="Verify Payment"/>
	<div id="verifyResult"></div>
</div>
```

`scripts/checkout.js`
```javascript
// Called on successful transaction
function setupVerify(pHookData) {

	console.log("setupVerify");
	console.log(pHookData);

	// Show verify container
	document.getElementById("verifyContainer").style.display = "block";

	// Set up verify call
	document.getElementById("verifyBtn").addEventListener("click", function() {

		// Disable verify button
		document.getElementById("verifyBtn").disabled = true;

		// Send data to server
		var url = "./cgi-bin/server_checkout.py";
		var postData = "endpoint=verify&payload=" + pHookData.payload;
		var headers = { "Content-Type": "application/x-www-form-urlencoded" };
		var method = "POST";

		AJAXPost(url + "?" + postData, headers, "POST", function() {
			// Display response
			document.getElementById("verifyResult").innerHTML = this.responseText;
		});
	});
}
```

### Completed javascript
Here it is, all together:

`script/checkout.js`
```javascript
// Custom text
var translationObject = {
    payButton: {
        "en-US": "Subscribe",
        "nl-NL": "Meer opties"
    }
};

// Customer styling for card fields
var styleObject = {
    base: {
        color: '#00F',
        fontSize: '14px',
        lineHeight: '14px',
        fontSmoothing: 'antialiased'
    },
    error: {
        color: 'red'
    },
    placeholder: {
        color: '#d8d8d8'
    },
    validated: {
        color: 'green'
    }
};

// Styling for larger Checkout object
var sdkConfigObj = {
	base: {
		fontSize: '16px',
		background: "#68FFC1",
		outline: "2px black",
		color: "blue",
	},
	paymentMethods: {
		card: {
			sfStyles: styleObject
		}
	},
	context: "test",
	translations: translationObject
};

// Add eventListener to Checkout button
function initPage() {
	document.getElementById("checkoutBtn").addEventListener("click", openCheckout);
}

// Collect setup data to send to server
function openCheckout() {
	var inputParams = document.querySelectorAll("input[type=text]");

	// Get request details from html form
	var formString = "";
	for (var param of inputParams) {
		formString = formString + param.name + "=" + param.value + "&";
	}
	formString = formString + "endpoint=setup";

	// Set parameters for request to server
	var url = "./cgi-bin/server_checkout.py";
	var headers = { "Content-Type": "application/x-www-form-urlencoded" };
	var method = "POST";

	// calls async javascript function to send to server
	AJAXPost(encodeURI(url + "?" + formString), headers, method, setupCallback);
}

// Send request to server
function AJAXPost(path, headers, method, callback) {

	// Initialize a request object
	var request = new XMLHttpRequest();
	request.open(method || "POST", path, true);

	// Tell the browser what to do when we get a response
	request.onreadystatechange = callback;

	// Iterate through headers and add to request object
	for (var key in headers) {
		request.setRequestHeader(key, headers[key]);
	}

	// Send request to server
	request.send({});
};

// Handle response from setup call
setupCallback = function() {

	// Only execute this function if the response is complete
	if (this.readyState == 4) {
		console.log(this);

		try {
			// Parse response to JSON object
			var data = JSON.parse(this.responseText);

			// Initialize checkout
			var checkout = chckt.checkout(data, '.checkout', sdkConfigObj);

			// Handle response from initiate call
			chckt.hooks.beforeComplete = function(pNode, pHookData, pData){
				setupVerify(pHookData);
				console.log(JSON.stringify(pData));
			}

			// Debug hooks
			chckt.hooks.beforeRedirect = function() {
				console.log("beforeRedirect");
			}
			chckt.hooks.beforePendingRedirect = function(selectedPMNode/*HTML Node*/, extraData/*Object*/) {
				console.log("beforePendingRedirect");
				selectedPMNode.style.opacity = '0.2';
				extraData.actionButton.style.opacity = '0.2';
				return false;
			};
		}
		catch (e) {
			console.log("error:");
			console.log(e);
			document.getElementById("checkout").innerHTML = this.responseText;
		}
	}
};

// Called on successful transaction
function setupVerify(pHookData) {

	console.log("setupVerify");
	console.log(pHookData);

	// Show verify container
	document.getElementById("verifyContainer").style.display = "block";

	// Set up verify call
	document.getElementById("verifyBtn").addEventListener("click", function() {

		// Disable verify button
		document.getElementById("verifyBtn").disabled = true;

		// Send data to server
		var url = "./cgi-bin/server_checkout.py";
		var postData = "endpoint=verify&payload=" + pHookData.payload;
		var headers = { "Content-Type": "application/x-www-form-urlencoded" };
		var method = "POST";

		AJAXPost(url + "?" + postData, headers, "POST", function() {
			// Display response
			document.getElementById("verifyResult").innerHTML = this.responseText;
		});
	});
}
```

## Section 5 - Checkout Backend
I'm also going to introduce a few more advanced concepts on the server, namely function calls and a rudimentary router.

### Routing requests
We're going to create a bare-bones router which associates an "endpoint" value from the request with a method defined by our server.  In a production environment you would use a framework like Flask or Django to route requests, but since we aren't worried about performance or security we can are going to use vanilla python to demonstrate the concept.

```python
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
```

### Checkout setup call
This should look very familiar by now - the request is basically the same as any other API call, except with different fields:

```python
def setup(data):

	# URL and headers
	url = "https://checkout-test.adyen.com/services/PaymentSetupAndVerification/setup"
	header_object = {
		"Content-Type": "application/json",
		"x-api-key": CHECKOUT_API_KEY
	}

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
```
Note that we don't have to make any changes on the server to use the AJAX we implemented on the front-end, all of that logic happens in the browser.

### Checkout verify call
Same logic, different API endpoint:

```python
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
```

### Finished backend
Putting back in the imports, static variables, and some extra fields which can be passed to /setup, here is the complete backend:

`cgi-bin/server_checkout.py`
```python
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
```
