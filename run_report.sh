#!/usr/bin/env bash
set -euo pipefail

PY=""

for candidate in python3 python py; do
    if command -v "$candidate" >/dev/null 2>&1 &&
       "$candidate" --version >/dev/null 2>&1; then
        PY="$candidate"
        break
    fi
done

if [ -z "$PY" ]; then
    echo "ERROR: no working Python interpreter found" >&2
    exit 1
fi

echo "Using interpreter: $PY"
export PYTHONPATH="src${PYTHONPATH:+:$PYTHONPATH}"

mkdir -p out

"$PY" -m orderly.cli seed --db out/orderly.db
mkdir -p out/reports
"$PY" -m orderly.cli report --db out/orderly.db --out out/reports

tar -czf out/reports.tar.gz -C out reports
tar -tzf out/reports.tar.gz

echo "run_report.sh finished"