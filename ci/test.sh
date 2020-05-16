#!/bin/bash
set -e

pyver_major=$(python -c 'import sys; print(sys.version_info[0])')
akind=$(python -c 'import sys; print("async" if sys.version_info[:2] > (3, 4) else "coro")')

coverage2=tests/cov2.ini
coverage3=tests/cov3-$akind.ini
coverage_key=coverage$pyver_major

python -m pytest \
  --cov covador \
  --cov-report term-missing \
  --cov-fail-under=100 \
  --cov-config ${!coverage_key} \
  tests \
  "$@"
