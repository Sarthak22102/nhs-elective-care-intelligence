# Statistical analysis and forecasting decision

The statistical layer prioritises interpretable diagnostics: lagged MoM/YoY change, rolling three-month flow, provider benchmarking, percentile ranks, consecutive deterioration streaks, outlier flags, practical gap sizes and sensitivity testing for any future composite pressure score.

The executed verification series contains only 12 monthly observations per entity. The project forecasting guard requires at least 24 valid monthly observations and adequate variation before models are compared. As a result, the verified snapshot correctly returns **not forecast-ready**. No ARIMA/ETS forecast, error metric or prediction interval is published from insufficient history.

After a successful full RTT history refresh, the intended evaluation is time-based: naive and seasonal-naive baselines first, then exponential smoothing and ARIMA/SARIMA only where history/seasonality justify them. Candidate models are compared on held-out future periods using MAE/RMSE and sMAPE where sensible, and prediction intervals are retained. Random train/test splits are not used for time series.
