"""
Tests for database write operations

These tests use in-memory SQLite for speed.
In production, you'd test against a test Postgres instance.
"""

import pandas as pd
import pytest
from sqlalchemy import create_engine, text


class TestDBWrites:
    """Test database write operations"""

    @pytest.fixture
    def temp_engine(self):
        """Create temporary in-memory SQLite database"""
        engine = create_engine("sqlite:///:memory:")
        yield engine
        engine.dispose()

    def test_write_forecast_table(self, temp_engine):
        """Test writing forecast data to database"""
        df = pd.DataFrame(
            {
                "ds": pd.date_range("2024-01-01", periods=5),
                "yhat": [100.0, 105.0, 110.0, 115.0, 120.0],
                "yhat_lower": [90.0, 95.0, 100.0, 105.0, 110.0],
                "yhat_upper": [110.0, 115.0, 120.0, 125.0, 130.0],
                "sku": ["SKU1"] * 5,
                "type": ["forecast"] * 5,
            }
        )

        # Write to database
        df.to_sql("simple_prophet_forecast", temp_engine, if_exists="replace", index=False)

        # Read back
        result = pd.read_sql("SELECT * FROM simple_prophet_forecast", temp_engine)

        assert len(result) == 5
        assert "ds" in result.columns
        assert "yhat" in result.columns
        assert "sku" in result.columns
        assert result["sku"].iloc[0] == "SKU1"

    def test_write_metrics_table(self, temp_engine):
        """Test writing metrics data to database"""
        df = pd.DataFrame(
            {
                "sku": ["SKU1", "SKU2", "SKU3"],
                "test_mae": [10.5, 12.3, 8.7],
                "test_rmse": [12.1, 14.5, 10.2],
                "test_mape_pct": [5.2, 6.1, 4.3],
                "test_bias": [2.1, -1.5, 0.8],
                "test_coverage_pct": [82.0, 79.5, 85.0],
                "n_train": [1000, 1000, 1000],
                "n_test": [30, 30, 30],
            }
        )

        # Write to database
        df.to_sql("forecast_error_metrics", temp_engine, if_exists="replace", index=False)

        # Read back
        result = pd.read_sql("SELECT * FROM forecast_error_metrics", temp_engine)

        assert len(result) == 3
        assert "sku" in result.columns
        assert "test_mae" in result.columns
        assert result["sku"].tolist() == ["SKU1", "SKU2", "SKU3"]

    def test_idempotent_writes(self, temp_engine):
        """Test that writing twice with if_exists='replace' is idempotent"""
        df1 = pd.DataFrame({"id": [1, 2, 3], "value": [10, 20, 30]})
        df2 = pd.DataFrame({"id": [1, 2], "value": [15, 25]})

        # First write
        df1.to_sql("test_table", temp_engine, if_exists="replace", index=False)
        result1 = pd.read_sql("SELECT * FROM test_table", temp_engine)
        assert len(result1) == 3

        # Second write (replaces)
        df2.to_sql("test_table", temp_engine, if_exists="replace", index=False)
        result2 = pd.read_sql("SELECT * FROM test_table", temp_engine)
        assert len(result2) == 2

    def test_table_columns_correct(self, temp_engine):
        """Test that created table has correct columns"""
        df = pd.DataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=3),
                "sku": ["A", "B", "C"],
                "value": [100, 200, 300],
            }
        )

        df.to_sql("test_table", temp_engine, if_exists="replace", index=False)

        # Check columns
        with temp_engine.connect() as conn:
            result = conn.execute(text("PRAGMA table_info(test_table)"))
            columns = [row[1] for row in result]

        assert "date" in columns
        assert "sku" in columns
        assert "value" in columns
        assert len(columns) == 3
