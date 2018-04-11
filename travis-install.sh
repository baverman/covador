#!/bin/sh

pip install pytest-cov==2.3.1
cat targets/$1/*/reqs.txt > /tmp/reqs.txt
pip install -r /tmp/reqs.txt -c targets/$1/cnst.txt
