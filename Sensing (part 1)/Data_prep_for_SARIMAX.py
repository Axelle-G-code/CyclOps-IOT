# data preparation for SARIMAX (including PCC and CCF calculation)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# load weather and traffic data
weather_data = pd.read_csv("weather_data.csv")
traffic_data = pd.read_csv("traffic_data.csv")

# ensure timestamps are aligned
weather_data["timestamp"] = pd.to_datetime(weather_data["timestamp"])
traffic_data["timestamp"] = pd.to_datetime(traffic_data["timestamp"])

# merge datasets on timestamp
merged_data = pd.merge(weather_data, traffic_data, on="timestamp", how="inner")

# calculate additional metrics for sarimax
merged_data["rain_intensity"] = merged_data["precipitation"] / (merged_data["wind_speed"] + 0.1)  # avoid div/0
merged_data["traffic_ratio"] = merged_data["current_speed"] / merged_data["free_flow_speed"]
merged_data["traffic_deviation"] = merged_data["free_flow_speed"] - merged_data["current_speed"]

# forward fill missing weather data to maintain continuity
merged_data.fillna(method="ffill", inplace=True)

# ensure no negative traffic speeds
merged_data["current_speed"] = merged_data["current_speed"].apply(lambda x: max(x, 0))

# add time-based features for seasonality
merged_data["hour"] = merged_data["timestamp"].dt.hour
merged_data["day_of_week"] = merged_data["timestamp"].dt.dayofweek

# calculate pearson correlation coefficient (pcc)
pcc = merged_data[["precipitation", "traffic_ratio"]].corr().iloc[0, 1]
print(f"Pearson correlation coefficient (pcc) between precipitation and traffic ratio: {pcc}")

# calculate cross-correlation function (ccf)
def cross_correlation(series1, series2, lag):
    return series1.corr(series2.shift(lag))

lags = range(-12, 13)  # test for lag values from -12 to 12 (hourly resolution)
ccf_values = [cross_correlation(merged_data["precipitation"], merged_data["traffic_ratio"], lag) for lag in lags]

# plot ccf
plt.figure(figsize=(10, 5))
plt.bar(lags, ccf_values, color="skyblue")
plt.axhline(y=0, color="black", linewidth=0.8, linestyle="--")
plt.title("Cross-Correlation Function (CCF) between Precipitation and Traffic Ratio")
plt.xlabel("Lag (hours)")
plt.ylabel("CCF Value")
plt.show()

# save prepared data for sarimax
merged_data.to_csv("Prepared_sarimax_data.csv", index=False)

print("Sarimax data preparation complete. data saved to prepared_sarimax_data.csv.")
