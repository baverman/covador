#!/bin/bash

pyversion=$1
shift
if [[ $pyversion == "2.7" || $pyversion == "pypy" ]]; then
    py.test tests --cov covador --cov-report term-missing --cov-fail-under=100 --cov-config cov-py2.ini "$@"
elif [[ $pyversion == "3.4" ]]; then
    py.test tests tests3.4 --cov covador --cov-report term-missing --cov-fail-under=100 --cov-config cov-py3.4.ini "$@"
else
    py.test --cov covador --cov-report term-missing --cov-fail-under=100 --cov-config cov-py3.ini "$@"
fi
