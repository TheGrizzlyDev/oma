#!/usr/bin/env bash
set -euo pipefail

RUNFILES_ROOT="${RUNFILES_DIR:-${BASH_SOURCE[0]}.runfiles}"
WORKSPACE_NAME="@WORKSPACE@"

image_path="${RUNFILES_ROOT}/${WORKSPACE_NAME}/@IMAGE_SHORT_PATH@"
geojson_path="${RUNFILES_ROOT}/${WORKSPACE_NAME}/@GEOJSON_SHORT_PATH@"
viewer_path="${RUNFILES_ROOT}/${WORKSPACE_NAME}/@VIEWER_SHORT_PATH@"
output_path="${PWD}/@OUTPUT_FILE@"

"${viewer_path}" \
  --image "${image_path}" \
  --geojson "${geojson_path}" \
  --bbox @BBOX@ \
  --output "${output_path}"

echo "Overlay written to ${output_path}"
