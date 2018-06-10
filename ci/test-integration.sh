#!/bin/bash
set -e
set -o pipefail

pyver=$(python -c 'import sys; print("{0}{1}".format(*sys.version_info[:2]))')

frameworks26="flask django tornado"
frameworks27="flask django tornado"
frameworks34="flask django tornado aiohttp_yield"
frameworks35="flask django tornado aiohttp_async sanic"
frameworks36="flask django tornado aiohttp_async sanic"

cover_flask=flask
cover_django=django
cover_tornado=tornado
cover_aiohttp_async=aiohttp
cover_aiohttp_yield=aiohttp
cover_sanic=sanic

flask26="flask==0.12.4 flask==1.0.2"
flask27="flask==0.12.4 flask==1.0.2"
flask34="flask==0.12.4 flask==1.0.2"
flask35="flask==0.12.4 flask==1.0.2"
flask36="flask==0.12.4 flask==1.0.2"

django26="django==1.4.22"
django27="django==1.4.22 django==1.9.13 django==1.11.13"
django34="django==1.9.13 django==1.11.13 django==2.0.6"
django35="django==1.9.13 django==1.11.13 django==2.0.6"
django36="django==1.9.13 django==1.11.13 django==2.0.6"

tornado26="tornado==3.2.2 tornado==4.3"
tornado27="tornado==3.2.2 tornado==4.5.3 tornado==5.0.2"
tornado34="tornado==3.2.2 tornado==4.5.3 tornado==5.0.2"
tornado35="tornado==3.2.2 tornado==4.5.3 tornado==5.0.2"
tornado36="tornado==3.2.2 tornado==4.5.3 tornado==5.0.2"

aiohttp_yield34="aiohttp==2.1.0"
aiohttp35="aiohttp==2.1.0 aiohttp==2.3.10 aiohttp==3.0.9 aiohttp==3.3.2"
aiohttp36="aiohttp==2.1.0 aiohttp==2.3.10 aiohttp==3.0.9 aiohttp==3.3.2"

sanic35="sanic==0.6.0 sanic==0.7.0"
sanic36="sanic==0.6.0 sanic==0.7.0"

frameworks_key=frameworks$pyver

for frm in ${!frameworks_key}; do
    f_key=${frm}${pyver}
    cover_key=cover_$frm
    for pkg in ${!f_key}; do
        echo
        echo "### Testing $pkg"
        pip install $PIP_OPTS --target=/tmp/covador-$pyver-$pkg $pkg | cat
        PYTHONPATH=$PYTHONPATH:/tmp/covador-$pyver-$pkg python -m pytest integration -k test_$frm
        COVERAGE_FILE=$frm.cov coverage report -m --fail-under=100 --include covador/${!cover_key}.py
    done
done
