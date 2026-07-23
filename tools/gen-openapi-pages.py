#!/usr/bin/env python3
"""Generate a GitBook API-reference page from an OpenAPI spec.

WHY THIS EXISTS
    The API pages are not hand-written prose — they are GitBook
    `openapi-operation` blocks that render live from a spec URL, so the schemas
    themselves can never go stale. What *does* go stale is the LIST of blocks:
    every endpoint needs one block, hand-typed. Add a route in code and the page
    silently omits it. That is exactly how the "current" Staff Portal API page
    drifted to 96 of 174 endpoints — hiding 45% of the surface from readers.

    This script emits the block list from the spec, so the page is complete by
    construction.

USAGE
    tools/gen-openapi-pages.py --spec <file|url> --spec-id <id> --spec-url <raw url>
                               --title <title> --description <desc>
                               --out <page.md> [--schemas]

    `--spec` is what we READ to enumerate operations; `--spec-url` is what the
    generated page POINTS AT (the raw URL GitBook fetches at render time). They
    are usually the same document reached two different ways.

REGENERATE (current pages)
    See tools/gen-openapi-pages.sh
"""

import argparse
import json
import sys
import urllib.request

# Only real HTTP operations; a path item may also carry `parameters`, `summary`
# etc., which are not operations and must not become blocks.
METHODS = ("get", "put", "post", "delete", "patch", "head", "options", "trace")


def load_spec(src: str) -> dict:
    if src.startswith(("http://", "https://")):
        with urllib.request.urlopen(src, timeout=30) as r:  # noqa: S310
            return json.load(r)
    with open(src) as fh:
        return json.load(fh)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True, help="spec to READ (file path or URL)")
    ap.add_argument("--spec-id", required=True, help='GitBook spec="" identifier')
    ap.add_argument("--spec-url", required=True, help="raw URL the page points at")
    ap.add_argument("--title", required=True)
    ap.add_argument("--description", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--schemas", action="store_true",
                    help="append an openapi-schemas block listing every component schema")
    args = ap.parse_args()

    spec = load_spec(args.spec)
    paths = spec.get("paths") or {}
    if not paths:
        print(f"ERROR: no paths in {args.spec}", file=sys.stderr)
        return 1

    ref = f"[OpenAPI {args.spec_id}]({args.spec_url})"
    out = [
        "---",
        f"description: {args.description}",
        "---",
        "",
        f"# {args.title}",
        "",
    ]

    n = 0
    # Spec order is FastAPI's router order, which groups related endpoints —
    # keep it rather than sorting alphabetically.
    for path, item in paths.items():
        for method in METHODS:
            if method not in item:
                continue
            out += [
                f'{{% openapi-operation spec="{args.spec_id}" path="{path}" method="{method}" %}}',
                ref,
                "{% endopenapi-operation %}",
                "",
            ]
            n += 1

    schemas = sorted((spec.get("components") or {}).get("schemas") or {})
    if args.schemas and schemas:
        out += [
            f'{{% openapi-schemas spec="{args.spec_id}" schemas="{",".join(schemas)}" grouped="true" %}}',
            ref,
            "{% endopenapi-schemas %}",
            "",
        ]

    with open(args.out, "w") as fh:
        fh.write("\n".join(out))

    print(f"  {args.out}: {n} operations across {len(paths)} paths"
          + (f", {len(schemas)} schemas" if args.schemas and schemas else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
