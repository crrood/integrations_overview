#!/bin/bash

source activate py2710
python -m CGIHTTPServer 8080
source deactivate