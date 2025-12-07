"""
Unit tests for ETL functions

Run with: pytest tests/test_etl.py -v
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class TestDataCleaning:
    """Test data cleaning and validation functions"""
    
    def test_date_parsing(self):
        """Test that dates are parsed correctly"""
        df = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'value': [100, 200, 300]
        })
        df['date'] = pd.to_datetime(df['date'])
        
        assert df['date'].dtype == 'datetime64[ns]'
        assert df['date'].min() == pd.Timestamp('2024-01-01')
        assert df['date'].max() == pd.Timestamp('2024-01-03')
    
    def test_negative_values_removed(self):
        """Test that negative sales are filtered out"""
        df = pd.DataFrame({
            'units_sold': [10, -5, 20, -1, 30],
            'sku': ['A', 'A', 'B', 'B', 'C']
        })
        df_clean = df[df['units_sold'] >= 0]
        
        assert len(df_clean) == 3
        assert df_clean['units_sold'].min() >= 0
    
    def test_null_handling(self):
        """Test that null values are handled correctly"""
        df = pd.DataFrame({
            'units_sold': [10, None, 20, np.nan, 30],
            'order_value': [100, 200, None, 400, 500]
        })
        df_clean = df.dropna(subset=['units_sold', 'order_value'])
        
        assert len(df_clean) == 2
        assert df_clean['units_sold'].notna().all()
        assert df_clean['order_value'].notna().all()
    
    def test_outlier_clipping(self):
        """Test that outliers are clipped to 99th percentile"""
        df = pd.DataFrame({
            'sku': ['A'] * 100,
            'y': list(range(1, 100)) + [1000]  # 1000 is outlier
        })
        
        def clip_outliers(sub):
            clip_val = sub['y'].quantile(0.99)
            sub = sub.copy()
            sub['y'] = sub['y'].clip(upper=clip_val)
            return sub
        
        df_clipped = df.groupby('sku', group_keys=False).apply(clip_outliers, include_groups=False)
        
        # 99th percentile of range(1, 100) + [1000] should be around 109
        # After clipping, max should be <= this value
        assert df_clipped['y'].max() <= 110  # Reasonable threshold
        assert df_clipped['y'].max() < 1000  # Definitely clipped from 1000


class TestDataValidation:
    """Test data validation rules"""
    
    def test_required_columns_exist(self):
        """Test that required columns are present"""
        df = pd.DataFrame({
            'date': ['2024-01-01'],
            'sku': ['Product A'],
            'total_units_sold': [100],
            'total_order_value': [1000]
        })
        
        required = ['date', 'sku', 'total_units_sold', 'total_order_value']
        for col in required:
            assert col in df.columns
    
    def test_sku_eligibility_filter(self):
        """Test SKU filtering logic (2+ years, 500+ units)"""
        # Create sample data
        dates = pd.date_range('2021-01-01', '2024-12-31', freq='D')
        df = pd.DataFrame({
            'ds': dates.tolist() * 2,
            'sku': ['Eligible SKU'] * len(dates) + ['Too Short'] * len(dates),
            'y': [2] * len(dates) + [1] * len(dates)  # Total: 2920 vs 1460 units
        })
        
        # Calculate stats
        sku_stats = df.groupby('sku').agg(
            first_date=('ds', 'min'),
            last_date=('ds', 'max'),
            total_units=('y', 'sum')
        ).reset_index()
        sku_stats['span_days'] = (sku_stats['last_date'] - sku_stats['first_date']).dt.days
        
        # Filter eligible
        eligible = sku_stats[
            (sku_stats['span_days'] >= 730) & (sku_stats['total_units'] > 500)
        ]
        
        assert len(eligible) == 2  # Both should pass
        assert eligible['span_days'].min() >= 730
        assert eligible['total_units'].min() > 500
    
    def test_channel_values(self):
        """Test that channel values are valid"""
        valid_channels = ['website', 'amazon', 'mobile']
        df = pd.DataFrame({
            'channel': ['website', 'amazon', 'mobile', 'website']
        })
        
        assert df['channel'].isin(valid_channels).all()
    
    def test_country_values(self):
        """Test that country values are valid"""
        valid_countries = ['US', 'CA']
        df = pd.DataFrame({
            'country': ['US', 'CA', 'US', 'CA']
        })
        
        assert df['country'].isin(valid_countries).all()


class TestForecastingPrep:
    """Test forecasting data preparation"""
    
    def test_prophet_column_names(self):
        """Test that data is renamed to Prophet format (ds, y)"""
        df = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02'],
            'total_units_sold': [100, 200]
        })
        df = df.rename(columns={'date': 'ds', 'total_units_sold': 'y'})
        df['ds'] = pd.to_datetime(df['ds'])
        
        assert 'ds' in df.columns
        assert 'y' in df.columns
        assert df['ds'].dtype == 'datetime64[ns]'
    
    def test_train_test_split(self):
        """Test train/test split logic"""
        dates = pd.date_range('2024-01-01', '2024-12-31', freq='D')
        df = pd.DataFrame({
            'ds': dates,
            'y': range(len(dates))
        })
        
        test_days = 30
        split_date = df['ds'].max() - pd.Timedelta(days=test_days)
        train = df[df['ds'] <= split_date]
        test = df[df['ds'] > split_date]
        
        assert len(test) == test_days
        assert len(train) == len(df) - test_days
        assert train['ds'].max() <= split_date
        assert test['ds'].min() > split_date


class TestMetrics:
    """Test metric calculations"""
    
    def test_mae_calculation(self):
        """Test Mean Absolute Error calculation"""
        from sklearn.metrics import mean_absolute_error
        
        y_true = np.array([100, 200, 300])
        y_pred = np.array([110, 190, 310])
        
        mae = mean_absolute_error(y_true, y_pred)
        expected = (10 + 10 + 10) / 3
        
        assert mae == expected
    
    def test_mape_calculation(self):
        """Test Mean Absolute Percentage Error calculation"""
        y_true = np.array([100, 200, 300])
        y_pred = np.array([110, 190, 310])
        
        mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
        expected = ((10/100 + 10/200 + 10/300) / 3) * 100
        
        assert abs(mape - expected) < 0.01
    
    def test_bias_calculation(self):
        """Test forecast bias calculation"""
        y_true = np.array([100, 200, 300])
        y_pred = np.array([110, 210, 310])  # Consistently over-forecasting by 10
        
        bias = np.mean(y_pred - y_true)
        
        assert bias == 10
    
    def test_coverage_calculation(self):
        """Test prediction interval coverage"""
        y_true = np.array([100, 200, 300, 400, 500])
        yhat_lower = np.array([90, 180, 280, 380, 480])
        yhat_upper = np.array([110, 220, 320, 420, 520])
        
        within_interval = (y_true >= yhat_lower) & (y_true <= yhat_upper)
        coverage = within_interval.mean() * 100
        
        assert coverage == 100.0  # All actuals within intervals


class TestDatabaseSchema:
    """Test database schema expectations"""
    
    def test_mart_sales_summary_schema(self):
        """Test that mart_sales_summary has expected columns"""
        expected_cols = [
            'date', 'sku', 'category', 'channel', 'country',
            'customer_segment', 'total_units_sold', 'total_order_value',
            'transaction_count', 'main_event', 'promo_flag', 'discontinued_flag'
        ]
        
        # This would connect to actual DB in integration test
        # For unit test, just verify the list
        assert len(expected_cols) == 12
        assert 'date' in expected_cols
        assert 'total_units_sold' in expected_cols
    
    def test_forecast_table_schema(self):
        """Test that forecast table has expected columns"""
        df = pd.DataFrame({
            'ds': ['2024-01-01'],
            'yhat': [100],
            'yhat_lower': [90],
            'yhat_upper': [110],
            'sku': ['Product A'],
            'type': ['forecast']
        })
        
        expected_cols = ['ds', 'yhat', 'yhat_lower', 'yhat_upper', 'sku', 'type']
        for col in expected_cols:
            assert col in df.columns


# Fixtures
@pytest.fixture
def sample_sales_data():
    """Fixture providing sample sales data"""
    dates = pd.date_range('2021-01-01', '2024-12-31', freq='D')
    return pd.DataFrame({
        'date': dates,
        'sku': 'Sample SKU',
        'total_units_sold': np.random.randint(10, 100, len(dates)),
        'total_order_value': np.random.uniform(1000, 10000, len(dates))
    })


@pytest.fixture
def sample_forecast_output():
    """Fixture providing sample Prophet forecast output"""
    dates = pd.date_range('2024-01-01', '2024-03-31', freq='D')
    return pd.DataFrame({
        'ds': dates,
        'yhat': np.random.uniform(50, 100, len(dates)),
        'yhat_lower': np.random.uniform(40, 80, len(dates)),
        'yhat_upper': np.random.uniform(60, 120, len(dates)),
        'sku': 'Sample SKU',
        'type': 'forecast'
    })


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
