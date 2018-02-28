#!/usr/local/adyen/python3/bin/python3

import cgi, sys

# respond with headers
sys.stdout.write("Content-type:application/json\r\n\r\n")

# send data for debugging
print(cgi.FieldStorage())