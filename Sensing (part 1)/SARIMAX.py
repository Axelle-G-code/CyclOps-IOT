# SARIMAX model training

import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error

# load prepared data
prepared_data = pd.read_csv("prepared_sarimax_data.csv")

# define features and target
endog = prepared_data["traffic_ratio"]  # target variable
exog = prepared_data[["precipitation", "temperature"]]  # exogenous variables

# train-test split
train_size = int(len(prepared_data) * 0.85)
train_endog = endog[:train_size]
train_exog = exog[:train_size]
test_endog = endog[train_size:]
test_exog = exog[train_size:]

# define sarimax parameters
p, d, q = 1, 1, 1
P, D, Q, m = 1, 1, 1, 288  # daily seasonality (5-min intervals)

# train sarimax model
print("training sarimax model...")
model = SARIMAX(train_endog, exog=train_exog, order=(p, d, q), seasonal_order=(P, D, Q, m))
model_fitted = model.fit(disp=False)

# diagnostics
print(model_fitted.summary())
model_fitted.plot_diagnostics(figsize=(10, 8))
plt.show()

# forecast
forecast = model_fitted.get_forecast(steps=len(test_endog), exog=test_exog)
forecast_mean = forecast.predicted_mean
confidence_intervals = forecast.conf_int()

# evaluate performance
mae = (forecast_mean - test_endog).abs().mean()
mse = mean_squared_error(test_endog, forecast_mean)
mape = ((forecast_mean - test_endog).abs() / test_endog.abs()).mean() * 100

print(f"mean absolute error (mae): {mae}")
print(f"mean squared error (mse): {mse}")
print(f"mean absolute percentage error (mape): {mape}%")

# plot forecast
plt.figure(figsize=(12, 6))
plt.plot(test_endog.index, test_endog, label="Observed", color="blue")
plt.plot(test_endog.index, forecast_mean, label="Forecast", color="orange")
plt.fill_between(test_endog.index, confidence_intervals.iloc[:, 0], confidence_intervals.iloc[:, 1], color="lightgray", alpha=0.5)
plt.title("SARIMAX Forecast vs Observed")
plt.legend()
plt.show()

# save model
model_fitted.save("sarimax_model.pkl")
print("sarimax model training complete. model saved to sarimax_model.pkl.")
