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