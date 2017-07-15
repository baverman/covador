#!/bin/bash
pip install pytest-cov==2.3.1 Flask
if [[ $1 == 3* ]]; then
    pip install aiohttp
fi
