from sqlalchemy import text

from db import get_engine

engine = get_engine()

with engine.connect() as conn:
    # Check views
    result = conn.execute(
        text(
            """
        SELECT table_name
        FROM information_schema.views
        WHERE table_schema='public'
          AND table_name LIKE 'v_forecast%'
        ORDER BY table_name
    """
        )
    )

    views = [row[0] for row in result]

    print("Stable Views Created:")
    for view in views:
        print(f"  ✓ public.{view}")

    # Sample data from forecast view
    result = conn.execute(
        text(
            """
        SELECT COUNT(*), MIN(forecast_date), MAX(forecast_date)
        FROM public.v_forecast_daily_latest
    """
        )
    )

    row = result.fetchone()
    print("\nView: v_forecast_daily_latest")
    print(f"  Rows: {row[0]:,}")
    print(f"  Date Range: {row[1]} to {row[2]}")

    # Sample metrics
    result = conn.execute(
        text(
            """
        SELECT COUNT(*), AVG(mean_absolute_pct_error)
        FROM public.v_forecast_sku_metrics_latest
    """
        )
    )

    row = result.fetchone()
    print("\nView: v_forecast_sku_metrics_latest")
    print(f"  SKUs: {row[0]}")
    print(f"  Avg MAPE: {row[1]:.1f}%")
