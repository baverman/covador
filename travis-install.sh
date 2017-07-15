#!/bin/bash
pip install pytest-cov==2.3.1 Flask tornado
if [[ $1 == 3* ]]; then
    pip install aiohttp
fi
