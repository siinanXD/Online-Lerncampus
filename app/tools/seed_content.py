"""CLI entry point for importing Python seed content into SQLite."""

from __future__ import annotations

import argparse

from app.core.config import get_settings
from app.services.content_seeder import ContentSeeder
from app.services.database import Database


def main() -> None:
    """Run the content seed importer."""
    parser = argparse.ArgumentParser(description="Import MAF seed content into SQLite.")
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
    args = parser.parse_args()

    settings = get_settings()
    database = Database(settings.database_url)
    seeder = ContentSeeder(database)

    if args.dry_run:
        print("empty=" + str(seeder.is_empty()))
        print(seeder.counts())
        return

    counts = seeder.seed_all(force=args.force)
    print("Seed import completed.")
    for key, value in counts.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
