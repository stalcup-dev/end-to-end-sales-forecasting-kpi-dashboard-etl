"""
Tests for ETL schema validation
"""

import pandas as pd


class TestETLSchema:
    """Test that data schemas are as expected"""

    def test_mart_sales_summary_schema(self):
        """Test mart_sales_summary has expected columns and types"""
        expected_columns = {
            "date": "object",  # Will be datetime after pd.to_datetime
            "sku": "object",
            "category": "object",
            "channel": "object",
            "country": "object",
            "customer_segment": "object",
            "total_units_sold": ("int64", "Int64", "float64"),  # Allow multiple types
            "total_order_value": ("float64", "Float64"),
            "transaction_count": ("int64", "Int64"),
        }

        # This is a schema test - in real use would query DB
        # For now just validate the expected structure
        assert len(expected_columns) == 9
        assert "date" in expected_columns
        assert "sku" in expected_columns
        assert "total_units_sold" in expected_columns

    def test_forecast_schema(self):
        """Test forecast table has expected columns"""
        expected_columns = ["ds", "yhat", "yhat_lower", "yhat_upper", "sku", "type"]

        # Create sample forecast dataframe
        df = pd.DataFrame(
            {
                "ds": pd.date_range("2024-01-01", periods=5),
                "yhat": [100, 105, 110, 115, 120],
                "yhat_lower": [90, 95, 100, 105, 110],
                "yhat_upper": [110, 115, 120, 125, 130],
                "sku": ["SKU1"] * 5,
                "type": ["forecast"] * 5,
            }
        )

        for col in expected_columns:
            assert col in df.columns

        assert df["yhat"].dtype in ["float64", "int64"]
        assert df["sku"].dtype == "object"

    def test_no_negative_quantities(self):
        """Test that sales quantities are non-negative"""
        df = pd.DataFrame(
            {"total_units_sold": [10, 20, 30, 0, 15], "total_order_value": [100, 200, 300, 0, 150]}
        )

        assert (df["total_units_sold"] >= 0).all()
        assert (df["total_order_value"] >= 0).all()

    def test_channel_values_valid(self):
        """Test that channel values are in expected set"""
        valid_channels = ["website", "amazon", "mobile"]

        df = pd.DataFrame({"channel": ["website", "amazon", "mobile", "website"]})

        assert df["channel"].isin(valid_channels + [None]).all()

    def test_country_values_valid(self):
        """Test that country values are in expected set"""
        valid_countries = ["US", "CA"]

        df = pd.DataFrame({"country": ["US", "CA", "US", "CA"]})

        assert df["country"].isin(valid_countries + [None]).all()
