from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import pickle
from datetime import datetime, timedelta

app = Flask(__name__)

# load models
hazard_model_path = "hazard_model.pkl"  # 3d hazard clustering model
traffic_model_path = "traffic_forecast_model.pkl"  # sarimax traffic model

with open(hazard_model_path, 'rb') as f:
    hazard_model = pickle.load(f)

with open(traffic_model_path, 'rb') as f:
    traffic_model = pickle.load(f)

# api endpoint: get directions
@app.route("/api/get-directions", methods=["POST"])
def get_directions():
    data = request.json
    start = data.get("start")
    end = data.get("end")

    # here you'd typically call an external api like openrouteservice for route directions
    # mock response for now
    directions = {
        "status": "success",
        "route": "mocked route from {} to {}".format(start, end),
    }
    return jsonify(directions)

# api endpoint: get weather and congestion predictions
@app.route("/api/get-weather-congestion", methods=["GET"])
def get_weather_congestion():
    # fetch past 24-hour weather and congestion data (15-min intervals)
    now = datetime.utcnow()
    timestamps = [now - timedelta(minutes=15 * i) for i in range(96)]
    timestamps.reverse()

    # simulate past data (normally fetched from a database or an api)
    weather_data = pd.DataFrame({
        "timestamp": timestamps,
        "temperature": np.random.uniform(10, 20, 96),
        "precipitation": np.random.uniform(0, 5, 96),
    })

    congestion_data = pd.DataFrame({
        "timestamp": timestamps,
        "speed": np.random.uniform(10, 25, 96),
    })

    # merge and preprocess for traffic forecasting model
    merged_data = pd.merge(weather_data, congestion_data, on="timestamp")
    forecast_input = merged_data[["temperature", "precipitation", "speed"]].tail(96)

    # predict traffic using the sarimax model
    traffic_forecast = traffic_model.forecast(steps=96, exog=forecast_input)

    # prepare response
    response = {
        "labels": [str(t) for t in timestamps[-96:]],
        "speeds": list(traffic_forecast),
    }
    return jsonify(response)

# api endpoint: hazard warnings
@app.route("/api/get-hazard-warnings", methods=["POST"])
def get_hazard_warnings():
    data = request.json
    gps_data = data.get("gps_data")  # expecting list of dicts: [{"latitude": ..., "longitude": ..., "proximity": ...}, ...]

    # convert to dataframe
    gps_df = pd.DataFrame(gps_data)

    # predict hazard clusters using the 3d hazard model
    labels = hazard_model.fit_predict(gps_df)
    gps_df["cluster"] = labels

    # identify hazards (cluster != -1)
    hazards = gps_df[gps_df["cluster"] != -1]

    # prepare response
    response = {
        "hazards": hazards.to_dict(orient="records"),
    }
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)
