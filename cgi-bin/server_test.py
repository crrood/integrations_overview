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
print(form.getvalue("testValue"))