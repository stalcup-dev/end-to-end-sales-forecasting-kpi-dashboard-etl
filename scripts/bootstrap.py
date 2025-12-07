#!/usr/bin/env python3
"""
Bootstrap script for Vita Markets database.

This script:
1. Checks if PostgreSQL is reachable
2. Creates schema and tables (idempotent)
3. Loads sample data from CSV into vitamarkets_raw
4. Prints row counts for verification

Usage:
    python scripts/bootstrap.py
"""

import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import text

# Add repo root to path to import db module
sys.path.insert(0, str(Path(__file__).parent.parent))
from db import get_engine

# Constants
ROOT = Path(__file__).parent.parent
SQL_INIT = ROOT / "sql" / "init.sql"
SAMPLE_DATA = ROOT / "vitamarkets_ultrarealistic_sampledataset.csv"


def check_db_connection(engine):
    """Test if database is reachable."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def run_init_sql(engine):
    """Run init.sql to create schema and tables (idempotent)."""
    print(f"\n📄 Running init.sql from {SQL_INIT}...")

    if not SQL_INIT.exists():
        raise FileNotFoundError(f"Init SQL file not found: {SQL_INIT}")

    sql_content = SQL_INIT.read_text()

    # Split on semicolons and execute each statement
    statements = [s.strip() for s in sql_content.split(";") if s.strip()]

    with engine.connect() as conn:
        for stmt in statements:
            # Skip psql-specific commands and comments
            if stmt.startswith("\\") or stmt.startswith("--") or not stmt:
                continue
            try:
                conn.execute(text(stmt))
            except Exception as e:
                # Some statements might fail if tables already exist, that's ok
                if "already exists" in str(e).lower():
                    continue
                # DROP TABLE CASCADE is expected to fail if table doesn't exist
                if "does not exist" in str(e).lower() and "DROP TABLE" in stmt:
                    continue
                print(f"⚠️  Statement failed (may be ok): {str(e)[:100]}")

        conn.commit()

    print("✅ Schema and tables created")


def load_sample_data(engine):
    """Load CSV data into vitamarkets_raw table."""
    print(f"\n📊 Loading sample data from {SAMPLE_DATA.name}...")

    if not SAMPLE_DATA.exists():
        raise FileNotFoundError(f"Sample data file not found: {SAMPLE_DATA}")

    # Read CSV
    df = pd.read_csv(SAMPLE_DATA)
    print(f"   → Loaded {len(df):,} rows from CSV")

    # Write to database (replace existing data for idempotency)
    df.to_sql(
        "vitamarkets_raw",
        engine,
        schema="public",
        if_exists="replace",  # Idempotent: always start fresh
        index=False,
        method="multi",
        chunksize=1000,
    )

    print(f"✅ Loaded {len(df):,} rows into vitamarkets_raw")


def print_row_counts(engine):
    """Print row counts for all tables."""
    print("\n📈 Table row counts:")

    tables = [
        "vitamarkets_raw",
        "mart_sales_summary",
        "simple_prophet_forecast",
        "forecast_error_metrics",
    ]

    with engine.connect() as conn:
        for table in tables:
            try:
                result = conn.execute(text(f"SELECT COUNT(*) FROM public.{table}"))
                count = result.scalar()
                print(f"   • {table}: {count:,} rows")
            except Exception:
                print(f"   • {table}: (table not found)")


def main():
    print("=" * 70)
    print("VITA MARKETS DATABASE BOOTSTRAP")
    print("=" * 70)

    # Get database engine
    engine = get_engine()

    # Step 1: Check connection
    if not check_db_connection(engine):
        print("\n❌ Bootstrap failed: Cannot connect to database")
        print("   Make sure PostgreSQL is running (docker compose up -d)")
        print("   and .env is configured correctly")
        sys.exit(1)

    # Step 2: Run init SQL
    try:
        run_init_sql(engine)
    except Exception as e:
        print(f"\n❌ Failed to run init SQL: {e}")
        sys.exit(1)

    # Step 3: Load sample data
    try:
        load_sample_data(engine)
    except Exception as e:
        print(f"\n❌ Failed to load sample data: {e}")
        sys.exit(1)

    # Step 4: Print verification
    print_row_counts(engine)

    print("\n" + "=" * 70)
    print("✅ BOOTSTRAP COMPLETE!")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. Run dbt: cd vitamarkets_dbt/vitamarkets && dbt run")
    print("  2. Run pipeline: python -m vitamarkets.pipeline --run-all")
    print("=" * 70)


if __name__ == "__main__":
    main()
