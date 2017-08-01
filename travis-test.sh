#!/bin/bash
pyversion=$1
shift
if [[ $pyversion == 3* ]]; then
    py.test --cov covador --cov-report term-missing --cov-fail-under=100 --cov-config cov-py3.ini "$@"
else
    py.test tests --cov covador --cov-report term-missing --cov-fail-under=100 --cov-config cov-py2.ini "$@"
fi
