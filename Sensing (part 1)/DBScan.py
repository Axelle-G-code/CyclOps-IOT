# dbscan model training and 3d hazard model generation

import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# load cleaned data
cleaned_data = pd.read_csv("cleaned_data.csv")

# extract relevant features
features = cleaned_data[["latitude_inflated", "longitude_inflated", "proximity_cm"]]

# parameter selection for dbscan
epsilon = 0.00018  # approx 18 meters (converted to lat/lon scale)
min_samples = 6  # minimum points to form a cluster

# train dbscan model
print("training dbscan model...")
dbscan_model = DBSCAN(eps=epsilon, min_samples=min_samples, metric='euclidean')
labels = dbscan_model.fit_predict(features)

# add cluster labels to the dataset
cleaned_data["cluster"] = labels

# filter out noise points (label = -1)
hazard_clusters = cleaned_data[cleaned_data["cluster"] != -1]

# visualize the clusters in 3d
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')
ax.scatter(
    hazard_clusters["latitude_inflated"],
    hazard_clusters["longitude_inflated"],
    hazard_clusters["proximity_cm"],
    c=hazard_clusters["cluster"],
    cmap="viridis",
    s=10
)

ax.set_xlabel("Latitude")
ax.set_ylabel("Longitude")
ax.set_zlabel("Proximity (cm)")
plt.title("3D Visualization of Hazard Clusters")
plt.show()

# save model outputs
hazard_clusters.to_csv("hazard_clusters.csv", index=False)
print("DBscan clustering complete. Hazard clusters saved to hazard_clusters.csv.")
