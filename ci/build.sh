#!/bin/bash
set -e
pyimage=${1:?Image is required}
user=$(id -u):$(id -g)

if [ -n "$PROXY" ]; then
    proxy_opts="--build-arg=http_proxy=$PROXY --build-arg=HTTP_PROXY=$PROXY"
fi

docker build --network=host $proxy_opts --build-arg IMAGE=$pyimage -t covador -f ci/Dockerfile.test build
find -name '*.pyc' -delete
test -t 1 && DTTY='-t'
docker run -i $DTTY --rm -w /build -u $user -v $PWD:/build -v /tmp:/tmp covador ./ci/test.sh
docker run -i $DTTY --rm -w /build \
           -e PIP_OPTS="--cache-dir=/tmp/pip_cache" \
           -u $user -v $PWD:/build -v /tmp:/tmp \
           covador ./ci/test-integration.sh

