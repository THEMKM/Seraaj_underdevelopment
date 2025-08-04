#!/usr/bin/env bash
set -euo pipefail

# Resolve script directory to repository root
DIR="$(cd "$(dirname "$0")"/.. && pwd)"

echo "=== Tracing ==="
echo "Running target enumeration..."
python "$DIR/scripts/enumerate_targets.py"

echo "Starting path tracing for discovered symbols..."
jq -r '.[].symbol' "$DIR/scripts/targets.json" | xargs -I{} -P4 claude "/agents use path-tracer symbol={}"

echo "=== Writing Issues ==="
echo "Processing implementation reports..."
if compgen -G "$DIR/ImplementationReports/traces/*.I.json" > /dev/null; then
    for rpt in "$DIR"/ImplementationReports/traces/*.I.json; do
        claude "/agents use issue-writer report_path=$rpt"
    done
else
    echo "No implementation reports found to process."
fi

echo "=== Aggregating ==="
echo "Running final aggregation..."
claude "/agents use aggregator"

echo "Path-tracing pipeline completed successfully."