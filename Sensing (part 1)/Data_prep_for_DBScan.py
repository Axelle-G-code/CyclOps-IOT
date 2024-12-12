# data cleaning script before dbscan

import pandas as pd
import numpy as np

# load raw data
raw_gps_data = pd.read_csv("gps_data.csv")
raw_proximity_data = pd.read_csv("proximity_data.csv")

# merge gps and proximity data on timestamp
merged_data = pd.merge(raw_gps_data, raw_proximity_data, on="timestamp")

# remove rows with missing or nan values
cleaned_data = merged_data.dropna()

# filter out implausible gps coordinates
# valid latitude range: -90 to 90, valid longitude range: -180 to 180
cleaned_data = cleaned_data[(cleaned_data["latitude"].between(-90, 90)) &
                            (cleaned_data["longitude"].between(-180, 180))]

# filter out proximity readings > 200 cm (threshold for hazards)
cleaned_data = cleaned_data[cleaned_data["proximity_cm"] <= 200]

# synchronize data streams using utc timestamps
cleaned_data = cleaned_data.sort_values(by="timestamp").reset_index(drop=True)

# handle gps gaps by forward-filling missing data
gps_columns = ["latitude", "longitude", "elevation"]
cleaned_data[gps_columns] = cleaned_data[gps_columns].fillna(method="ffill")

# inflate gps points to create hazard geofences
cleaned_data["latitude_inflated"] = cleaned_data["latitude"] + np.random.uniform(-0.0001, 0.0001, size=len(cleaned_data))
cleaned_data["longitude_inflated"] = cleaned_data["longitude"] + np.random.uniform(-0.0001, 0.0001, size=len(cleaned_data))

# smooth gps jitter by applying rolling average
cleaned_data["latitude"] = cleaned_data["latitude"].rolling(window=3, min_periods=1).mean()
cleaned_data["longitude"] = cleaned_data["longitude"].rolling(window=3, min_periods=1).mean()

# save cleaned data to new csv
cleaned_data.to_csv("cleaned_data.csv", index=False)

print("data cleaning complete. cleaned data saved to cleaned_data.csv.")
