"""CLI entry point for importing Python or JSON seed content."""

from __future__ import annotations

import argparse
from pathlib import Path

from app.core.config import get_settings
from app.data.content_bundle import load_json_bundle, load_python_bundle
from app.data.jsonl_dataset import load_jsonl_dataset
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
        choices=("python", "json", "jsonl"),
        default=None,
        help="Override CONTENT_SEED_FORMAT for this run.",
    )
    parser.add_argument(
        "--json-path",
        type=Path,
        default=None,
        help="Override CONTENT_JSON_BUNDLE_PATH for this run.",
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=None,
        help="BZE MAF JSONL ZIP or directory to import.",
    )
    parser.add_argument(
        "--approve",
        action="store_true",
        help="Mark imported learning content as approved.",
    )
    args = parser.parse_args()

    settings = get_settings()
    seed_format = args.format or settings.content_seed_format
    database = create_database(settings.database_url)
    if args.dataset is not None:
        bundle = load_jsonl_dataset(args.dataset)
    elif seed_format == "jsonl":
        json_path = args.json_path or Path(settings.content_json_bundle_path)
        bundle = load_jsonl_dataset(json_path)
    elif seed_format == "json":
        json_path = args.json_path or Path(settings.content_json_bundle_path)
        bundle = load_json_bundle(json_path)
    else:
        bundle = load_python_bundle()
    seeder = ContentSeeder(database, bundle=bundle)

    if args.dry_run:
        print("empty=" + str(seeder.is_empty()))
        print(seeder.counts())
        print(
            "bundle="
            + str(
                {
                    "units": len(bundle.units),
                    "quiz_questions": len(bundle.questions),
                    "open_questions": len(bundle.open_questions),
                    "exams": len(bundle.exams),
                    "categories": len(bundle.categories),
                    "sources": len(bundle.sources),
                }
            )
        )
        return

    counts = seeder.seed_all(force=args.force)
    if args.approve or not settings.content_review_required:
        database.approve_all_content()
    from app.services.platform_seeder import PlatformSeeder

    platform_counts = PlatformSeeder(database).seed_all(force=args.force)
    print("Seed import completed.")
    for key, value in counts.items():
        print(f"  {key}: {value}")
    print("Platform tools:")
    for key, value in platform_counts.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
