#!/bin/bash

function version_gt() {
    test "$(printf '%s\n' "$@" | sort -V | head -n 1)" != "$1";
}

pyversion=$1
shift
if version_gt $pyversion 3.4; then
    py.test --cov covador --cov-report term-missing --cov-fail-under=100 --cov-config cov-py_3.4.ini "$@"
elif [[ $pyversion == 3*  ]]; then
    py.test tests tests3 --cov covador --cov-report term-missing --cov-fail-under=100 --cov-config cov-py3.ini "$@"
else
    py.test tests --cov covador --cov-report term-missing --cov-fail-under=100 --cov-config cov-py2.ini "$@"
fi
