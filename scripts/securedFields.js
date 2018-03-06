// Global vars
var globals = {};

// Config object
globals.securedFieldsConfiguration = {
	configObject : {
		originKey: "YOUR_ORIGIN_KEY", // Comes from the setupResponseJSON object.
		publicKeyToken : "YOUR_PUBLIC_KEY_TOKEN" // Comes from the setupResponseJSON object.
	},
	rootNode: '.secured-fields-form'
};

// Event listeners async form submissions
function initForms() {
	document.getElementById("setupBtn").addEventListener("click", setupSecuredFields);
	document.getElementById("checkoutBtn").addEventListener("click", submitPayment);

	globals.brandImage = document.getElementById("brand-container");
}

// Helper method for log output
function displayToWindow(text) {
	document.getElementById("output").innerHTML = document.getElementById("output").innerHTML + "<br>" + text;
}

// Called on submitting payment data form
function setupSecuredFields(e) {
	e.preventDefault();

	var inputParams = document.querySelectorAll("input[class=payment-data]");

	// Get request details from html form
	var formString = "";
	for (var param of inputParams) {
		formString = formString + param.name + "=" + param.value + "&";
	}
	formString = formString + "endpoint=setup";

	// Set parameters for request to server
	url = "cgi-bin/server_checkout.py";
	headers = { "Content-Type": "application/x-www-form-urlencoded" };
	method = "POST";

	// calls async javascript function to send to server
	AJAXPost(encodeURI(url + "?" + formString), headers, {}, method);
}

// Handle response from setup call
callback = function() {

	if (this.readyState == 4) {
		console.log("response:" );
		console.log(this);

		try {

			// Parse data
			globals.data = JSON.parse(this.responseText);
			globals.securedFieldsConfiguration.configObject.originKey = globals.data.originKey;
			globals.securedFieldsConfiguration.configObject.publicKeyToken = globals.data.publicKeyToken;

			console.log(globals.data);

			// Initialize secured fields
			globals.securedFields = csf(globals.securedFieldsConfiguration);

			console.log(globals.securedFields);

			// Set initial 'generic' card logo
			globals.brandImage.setAttribute("src", globals.data.logoBaseUrl + "card@2x.png");

			globals.securedFields.onBrand( function(brandObject){

				// Triggered when receiving a brand callback from the credit card number validation.
				if (brandObject.brand) {
					globals.brandImage.setAttribute("src", globals.data.logoBaseUrl + brandObject.brand + "@2x.png");
					globals.paymentMethodType = brandObject.brand;
				}
			});

			// Un-gray out the entry fields
			document.getElementById("secured-fields-container").classList.remove("inactive");
		}
		catch (e) {
			console.log(e);
			document.getElementById("output").innerHTML = e;
		}
	}
};

// Called from JS library on successful payment
function paymentSuccess(result) {
	if (result.type === "complete") {
		document.getElementById("secured-fields-container").remove();
		if (result.resultCode === "authorised") {
			displayToWindow("Success!");
		}
		else {
			displayToWindow("Failure");
		}
	}
	displayToWindow(JSON.stringify(result));
}

// Called from JS library on failed payment
function paymentError(result) {
	displayToWindow("Error!");
	displayToWindow(result);
}

// Send payment using info from SecuredFields
function submitPayment(e) {
	e.preventDefault();

	console.log(globals.securedFields);

	// Configuration object
	var initPayConfig = {
		responseData : globals.data, // This is the JSON object you received from the ‘setup’ call to the Checkout API.
		pmType : globals.paymentMethodType, // e.g. ‘visa’,’mc’, ‘amex’.
		formEl : document.getElementById("adyen-encrypted-form"), // The <form> element that holds your securedFields.
		onSuccess : paymentSuccess, // Callback function for the AJAX call that checkoutInitiatePayment makes.
		onError : paymentError // Callback function function for the AJAX call that checkoutInitiatePayment makes.
	};

	displayToWindow("sending payment...")
	
	// Sends data to server
	// Using method from JS library
	var res = chcktPay(initPayConfig);
}

// Send request to server
function AJAXPost(path, headers, params, method) {
	var request = new XMLHttpRequest();
	request.open(method || "POST", path, true);
	request.onreadystatechange = callback;

	for (var key in headers) {
		request.setRequestHeader(key, headers[key]);
	}

	request.send(params);
};
