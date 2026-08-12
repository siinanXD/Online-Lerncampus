"""Export the Python MAF seed bundle to JSON for Phase 7 authoring."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.data.content_bundle import bundle_to_json, default_json_bundle_path, load_python_bundle


def main() -> None:
    """Write the default MAF bundle JSON file."""
    parser = argparse.ArgumentParser(description="Export MAF content bundle to JSON.")
    parser.add_argument(
        "--output",
        type=Path,
        default=default_json_bundle_path(),
        help="Target JSON file path.",
    )
    args = parser.parse_args()
    bundle = load_python_bundle()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(bundle_to_json(bundle), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Exported bundle to {args.output}")


if __name__ == "__main__":
    main()
