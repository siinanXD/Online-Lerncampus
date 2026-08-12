"""CLI entry point for importing Python or JSON seed content."""

from __future__ import annotations

import argparse
from pathlib import Path

from app.core.config import get_settings
from app.data.content_bundle import load_json_bundle, load_python_bundle
from app.services.content_seeder import ContentSeeder
from app.services.database import create_database


def main() -> None:
    """Run the content seed importer."""
    parser = argparse.ArgumentParser(description="Import MAF seed content.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Delete existing content rows before importing.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only report whether the database is empty.",
    )
    parser.add_argument(
        "--format",
        choices=("python", "json"),
        default=None,
        help="Override CONTENT_SEED_FORMAT for this run.",
    )
    parser.add_argument(
        "--json-path",
        type=Path,
        default=None,
        help="Override CONTENT_JSON_BUNDLE_PATH for this run.",
    )
    args = parser.parse_args()

    settings = get_settings()
    seed_format = args.format or settings.content_seed_format
    database = create_database(settings.database_url)
    if seed_format == "json":
        json_path = args.json_path or Path(settings.content_json_bundle_path)
        bundle = load_json_bundle(json_path)
    else:
        bundle = load_python_bundle()
    seeder = ContentSeeder(database, bundle=bundle)

    if args.dry_run:
        print("empty=" + str(seeder.is_empty()))
        print(seeder.counts())
        return

    counts = seeder.seed_all(force=args.force)
    if not settings.content_review_required:
        database.approve_all_content()
    print("Seed import completed.")
    for key, value in counts.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
