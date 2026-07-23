#!/usr/bin/env bash
# Regenerate the Registry API reference pages from the OpenAPI specs published
# by registry-platform.
#
# LAYOUT
#   <api-documentation>/                 CURRENT — tracks `develop`, regenerate freely
#   <api-documentation>/<N.N.N>/         FROZEN  — pinned to a release ref
#
# The frozen snapshots are generated ONCE, when the release is cut, and then left
# alone; they are re-emitted here only so every page is generated rather than
# hand-typed. Re-running this script is safe: a frozen ref yields the same output.
#
# Run from the repo root:  bash tools/gen-openapi-pages.sh
set -euo pipefail

REPO="https://raw.githubusercontent.com/OpenG2P/registry-platform"
OUT="products/registry/registry/developer-zone/api-documentation"

# gen <ref> <output-dir> <spec-id-suffix>
gen() {
  local ref="$1" dir="$2" sfx="$3" base="${REPO}/$1/apis/docs/openapi"
  mkdir -p "$dir"
  python3 tools/gen-openapi-pages.py \
    --spec "${base}/openapi-staff-portal.json" \
    --spec-id "registry-staff-portal-api${sfx}" \
    --spec-url "${base}/openapi-staff-portal.json" \
    --title "Staff Portal API" \
    --description "APIs used by the Staff Portal UI" \
    --out "${dir}/staff-portal-api.md"

  python3 tools/gen-openapi-pages.py \
    --spec "${base}/openapi-partner.json" \
    --spec-id "registry-partner-api${sfx}" \
    --spec-url "${base}/openapi-partner.json" \
    --title "Partner API" \
    --description "APIs available for the Registry Partner ecosystem" \
    --out "${dir}/partner-api.md" \
    --schemas
}

echo "CURRENT (develop)"
gen develop "${OUT}" ""

# To cut a FROZEN snapshot at release time (once the spec is regenerated per
# release — see the note in README.md), add a line like:
#   gen 1.2.0 "${OUT}/1.2.0" "-120"
# and list it in SUMMARY.md. There is no point doing this while every release ref
# carries the same spec.

echo "Done."
