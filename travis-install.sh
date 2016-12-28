#!/bin/bash
pip install pytest-cov==2.3.1
if [[ $1 == 3* ]]; then
    pip install aiohttp
    pip install pytest-aiohttp
fi
