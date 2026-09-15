import numpy as np
import pandas as pd
import pytest

from nhs_elective_intelligence.forecasting.models import (
    assess_forecast_readiness, error_metrics, naive_forecast, seasonal_naive_forecast,
)


def test_short_series_not_forecast_ready():
    result=assess_forecast_readiness(pd.Series(range(12)),minimum_months=24)
    assert not result.ready
    assert result.observations==12


def test_naive_forecast_repeats_last_value():
    assert naive_forecast(pd.Series([1,2,3]),3).tolist()==[3,3,3]


def test_seasonal_naive_requires_complete_season():
    with pytest.raises(ValueError):
        seasonal_naive_forecast(pd.Series(range(6)),2,season=12)


def test_error_metrics_exact_prediction_zero_error():
    metrics=error_metrics(np.array([1,2]),np.array([1,2]))
    assert metrics=={"mae":0.0,"rmse":0.0,"smape":0.0}
