#!/bin/bash
pip install pytest-cov==2.3.1 Flask tornado WebOb Django
if [[ $1 == 3* ]]; then
    pip install aiohttp
    if [[ $1 == 3.5* ]]; then
        pip install sanic
        pip install pytest-sanic
    fi
fi
