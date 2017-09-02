#!/bin/bash
pip install pytest-cov==2.3.1 Flask tornado WebOb Django
if [[ $1 == 3* ]]; then
    pip install aiohttp
    pip install pytest-sanic
fi
