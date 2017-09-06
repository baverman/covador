#!/bin/bash

pyversion=$1
shift

exec python -m pytest \
  --cov covador \
  --cov-report term-missing \
  --cov-fail-under=100 \
  --cov-config targets/$pyversion/cov.ini \
  targets/$pyversion \
  "$@"
