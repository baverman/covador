#!/bin/sh
exec py.test --cov covador --cov-report html --cov-config cov-py2.ini $@
