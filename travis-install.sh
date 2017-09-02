#!/bin/bash

function version_gt() {
    test "$(printf '%s\n' "$@" | sort -V | head -n 1)" != "$1";
}

pip install pytest-cov==2.3.1 Flask tornado WebOb Django
if [[ $1 == 3* ]]; then
    pip install aiohttp
    if [[ version_gt $pyversion 3.4 ]]; then
        pip install sanic
        pip install pytest-sanic
    fi
fi
