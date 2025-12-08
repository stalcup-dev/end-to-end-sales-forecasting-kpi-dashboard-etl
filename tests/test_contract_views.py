import pytest
from sqlalchemy import inspect

from db import get_engine


@pytest.fixture(scope="module")
def pg_engine():
    try:
        engine = get_engine()
    except Exception:
        pytest.skip("Database not configured for contract check")
    if engine.dialect.name != "postgresql":
        pytest.skip("Contract check requires PostgreSQL")
    return engine


def _assert_columns(engine, schema, table_name, required):
    inspector = inspect(engine)
    if table_name not in inspector.get_view_names(schema=schema):
        pytest.skip(f"{schema}.{table_name} view not found")
    cols = {col["name"] for col in inspector.get_columns(table_name, schema=schema)}
    missing = required - cols
    assert not missing, f"Missing columns in {schema}.{table_name}: {sorted(missing)}"


def test_simple_prophet_forecast_columns(pg_engine):
    required = {"ds", "sku", "yhat", "yhat_lower", "yhat_upper", "data_type", "forecast_run_id"}
    _assert_columns(pg_engine, "public", "simple_prophet_forecast", required)


def test_forecast_error_metrics_columns(pg_engine):
    required = {"sku", "test_mae", "test_rmse", "test_mape_pct", "test_bias", "test_coverage_pct", "n_train", "n_test", "run_id"}
    _assert_columns(pg_engine, "public", "forecast_error_metrics", required)
