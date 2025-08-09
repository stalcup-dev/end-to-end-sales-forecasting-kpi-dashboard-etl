# etl/refresh_actuals.py
import os
import pandas as pd
from sqlalchemy import text
from db import get_engine  # <- central, secure DB connector (loads .env inside)

def load_actuals(csv_path: str = "data/actuals_latest.csv") -> int:
    """
    Read the latest actuals CSV, validate/clean, and load into public.mart_sales_summary.
    Returns the number of rows loaded.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Actuals file not found: {csv_path}")

    # 1) Extract
    df = pd.read_csv(csv_path)

    # 2) Validate & basic cleaning (adjust to your columns as needed)
    # Expected columns: date, sku, channel, country, customer_segment,
    #                   total_units_sold, total_order_value, main_event, promo_flag
    required = [
        "date", "sku", "channel", "country", "customer_segment",
        "total_units_sold", "total_order_value"
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in actuals CSV: {missing}")

    # Types & cleaning
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    df = df[df["total_units_sold"].notna() & (df["total_units_sold"] >= 0)]
    df = df[df["total_order_value"].notna() & (df["total_order_value"] >= 0)]

    # Optional: fix precision (e.g., money column)
    df["total_order_value"] = df["total_order_value"].round(2)

    # 3) Load (replace or upsert; here: replace for demo)
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("SET search_path TO public;"))
        # if_exists="replace" matches your original behavior; switch to "append" for incremental loads
        df.to_sql(
            "mart_sales_summary",
            con=conn,
            if_exists="replace",
            index=False,
            chunksize=10_000,      # friendly for larger files
            method="multi"
        )

    print(f"[OK] Loaded {len(df):,} rows into public.mart_sales_summary")
    return len(df)

if __name__ == "__main__":
    load_actuals()
