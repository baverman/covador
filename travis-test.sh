#!/bin/bash
pyversion=$1
shift
if [[ $pyversion == 3.[0-4]* ]]; then
    py.test tests tests3 --cov covador --cov-report term-missing --cov-fail-under=100 --cov-config cov-py3.ini "$@"
elif [[ $pyversion == 3.[5-9]*  ]]; then
    py.test --cov covador --cov-report term-missing --cov-fail-under=100 --cov-config cov-py3.ini "$@"
else
    py.test tests --cov covador --cov-report term-missing --cov-fail-under=100 --cov-config cov-py2.ini "$@"
fi
