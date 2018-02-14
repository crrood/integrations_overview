#!/usr/bin/python

# imports
import sys			## format printing of HTTP response
import cgi, cgitb	## handle server requests

# enable debugging cgi errors from the browser
cgitb.enable()

# method to include headers in HTTP response
def send_headers(content_type="text/json"):
	sys.stdout.write("Content-type:{}\r\n".format(content_type))
	sys.stdout.write("\r\n")

# parse payment data from URL params 
form = cgi.FieldStorage()

# respond with headers
send_headers()

# send data for debugging
print form
print form.getvalue("testValue")