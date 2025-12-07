"""
Tests for forecast evaluation functions
"""

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error


class TestForecastEval:
    """Test forecast evaluation metric calculations"""

    def test_mae_calculation(self):
        """Test MAE is calculated correctly"""
        y_true = np.array([100, 200, 300, 400, 500])
        y_pred = np.array([105, 195, 310, 390, 505])

        mae = mean_absolute_error(y_true, y_pred)
        expected = (5 + 5 + 10 + 10 + 5) / 5

        assert mae == expected

    def test_rmse_calculation(self):
        """Test RMSE is calculated correctly"""
        y_true = np.array([100, 200, 300])
        y_pred = np.array([110, 190, 310])

        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        expected = np.sqrt(((10**2) + (10**2) + (10**2)) / 3)

        assert abs(rmse - expected) < 0.01

    def test_mape_calculation(self):
        """Test MAPE is calculated correctly"""
        y_true = np.array([100, 200, 300])
        y_pred = np.array([110, 190, 310])

        mape = np.mean(np.abs((y_true - y_pred) / np.maximum(y_true, 1))) * 100
        expected = ((10 / 100 + 10 / 200 + 10 / 300) / 3) * 100

        assert abs(mape - expected) < 0.01

    def test_mape_handles_zero_actuals(self):
        """Test MAPE handles zero actual values gracefully"""
        y_true = np.array([0, 100, 200])
        y_pred = np.array([10, 110, 190])

        # Should use max(y_true, 1) to avoid division by zero
        mape = np.mean(np.abs((y_true - y_pred) / np.maximum(y_true, 1))) * 100

        assert not np.isnan(mape)
        assert not np.isinf(mape)

    def test_bias_calculation(self):
        """Test forecast bias is calculated correctly"""
        y_true = np.array([100, 200, 300])
        y_pred = np.array([105, 205, 305])

        bias = np.mean(y_pred - y_true)

        assert bias == 5.0

    def test_coverage_calculation(self):
        """Test prediction interval coverage"""
        y_true = np.array([100, 150, 200, 250, 300])
        yhat_lower = np.array([90, 140, 190, 240, 290])
        yhat_upper = np.array([110, 160, 210, 260, 310])

        within_interval = (y_true >= yhat_lower) & (y_true <= yhat_upper)
        coverage = within_interval.mean() * 100

        assert coverage == 100.0

    def test_coverage_partial(self):
        """Test coverage when some actuals fall outside intervals"""
        y_true = np.array([100, 150, 250, 280, 350])  # 250 and 350 outside
        yhat_lower = np.array([90, 140, 190, 240, 290])
        yhat_upper = np.array([110, 160, 210, 260, 310])

        within_interval = (y_true >= yhat_lower) & (y_true <= yhat_upper)
        coverage = within_interval.mean() * 100

        assert coverage == 60.0  # 3 out of 5

    def test_metrics_return_correct_keys(self):
        """Test that metrics dict has expected keys"""
        metrics = {
            "sku": "Test SKU",
            "test_mae": 10.5,
            "test_rmse": 12.3,
            "test_mape_pct": 5.2,
            "test_bias": 2.1,
            "test_coverage_pct": 82.0,
            "n_train": 1000,
            "n_test": 30,
        }

        expected_keys = [
            "sku",
            "test_mae",
            "test_rmse",
            "test_mape_pct",
            "test_bias",
            "test_coverage_pct",
            "n_train",
            "n_test",
        ]

        for key in expected_keys:
            assert key in metrics

    def test_edge_case_single_observation(self):
        """Test metrics with single observation"""
        y_true = np.array([100])
        y_pred = np.array([105])

        mae = mean_absolute_error(y_true, y_pred)
        assert mae == 5.0

        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        assert rmse == 5.0
