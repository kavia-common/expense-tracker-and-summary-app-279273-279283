"""Entry point to initialize the database: `python -m src.db`.

This will:
- Create all tables if they do not exist.
- Seed demo data idempotently (safe to re-run).
Use flags:
  --no-schema  to skip schema creation
  --no-seed    to skip seeding
"""
from __future__ import annotations

import argparse

from src.db.init_db import init_db


def main() -> None:
    """Parse args and initialize database."""
    parser = argparse.ArgumentParser(description="Initialize database schema and seed data.")
    parser.add_argument("--no-schema", action="store_true", help="Do not create schema.")
    parser.add_argument("--no-seed", action="store_true", help="Do not insert seed data.")
    args = parser.parse_args()

    init_db(create_schema=not args.no_schema, seed=not args.no_seed)


if __name__ == "__main__":
    main()
