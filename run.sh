#!/usr/bin/env bash
set -euo pipefail
soundsausage_project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd -- "$soundsausage_project_dir"
make --no-print-directory all
export PYTHONPATH="$soundsausage_project_dir/src${PYTHONPATH:+:$PYTHONPATH}"
exec python3 -m soundsausage "$@"
