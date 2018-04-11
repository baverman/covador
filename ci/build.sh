#!/bin/bash
set -e
pyimage=${1:?Image is required}
pyver=${2:?Version is required}
tar -hcf - --sort=name ci/Dockerfile.test travis-install.sh targets/$pyver/*/reqs.txt targets/$pyver/cnst.txt \
    | docker build --build-arg IMAGE=$pyimage --build-arg PYVERSION=$pyver -t covador-$pyver -f ci/Dockerfile.test -
find -name '*.pyc' -delete
docker run --rm -w /build -e PYTHONPATH=/build -u $UID:$GROUPS -v $PWD:/build covador-$pyver ./travis-test.sh $pyver
