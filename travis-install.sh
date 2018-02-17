#!/bin/sh

pip install pytest-cov==2.3.1
ls targets/$1/*/reqs.txt | xargs -n1 pip install -r
