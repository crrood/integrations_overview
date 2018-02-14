# integration_overview
Step by step integration with Adyen test server

## Setup:
Add authentication credentials to /cgi-bin/submit.py

## Start
```shell
python -m CGIHTTPServer 8000
```

Then go to localhost:8000 in your browser

## Troubleshooting
If you get permission problems, run
```shell
chmod +x cgi-bin/server.py
```