#!/bin/sh
export PYTHONPATH=/usr/lib/soundsausage/src
export PYTHONDONTWRITEBYTECODE=1
exec /usr/bin/python3 -m soundsausage "$@"
