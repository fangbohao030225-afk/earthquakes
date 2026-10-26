# The Python standard library includes some functionality for communicating
# over the Internet.
# However, we will use a more powerful and simpler library called requests.
# This is external library that you may need to install first.
import requests
import json
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime


def get_data():
    # With requests, we can ask the web service for the data.
    # Can you understand the parameters we are passing here?
    response = requests.get(
        "http://earthquake.usgs.gov/fdsnws/event/1/query.geojson",
        params={
            'starttime': "2000-01-01",
            "maxlatitude": "58.723",
            "minlatitude": "50.008",
            "maxlongitude": "1.67",
            "minlongitude": "-9.756",
            "minmagnitude": "1",
            "endtime": "2018-10-11",
            "orderby": "time-asc"}
    )

    text = response.text
    data = json.loads(text)
    return data


def count_earthquakes(data):
    """Get the total number of earthquakes in the response."""
    return len(data["features"])


def get_magnitude(earthquake):
    """Retrive the magnitude of an earthquake item."""
    return earthquake["properties"]["mag"]


def get_location(earthquake):
    """Retrieve the latitude and longitude of an earthquake item."""
    # coordinates: [longitude, latitude, depth]
    coordinates = earthquake["geometry"]["coordinates"]
    lat = coordinates[1]
    lon = coordinates[0]
    return lat, lon


def get_maximum(data):
    """Get the magnitude and location of the strongest earthquake in the data."""
    max_mag = -1.0
    max_pos = None
    for quake in data["features"]:
        mag = get_magnitude(quake)
        if mag > max_mag:
            max_mag = mag
            max_pos = get_location(quake)
    return max_mag, max_pos


# 新增：提取每一条地震的【年份】和【震级】
def extract_year_mag(data):
    years = []
    magnitudes = []
    for quake in data["features"]:
        # time 是毫秒时间戳
        time_ms = quake["properties"]["time"]
        time_sec = time_ms / 1000
        dt = datetime.fromtimestamp(time_sec)
        year = dt.year
        mag = get_magnitude(quake)
        years.append(year)
        magnitudes.append(mag)
    return np.array(years), np.array(magnitudes)

def plot_annual_count(years, magnitudes):
    # 统计每年地震数量
    unique_years, counts = np.unique(years, return_counts=True)
    plt.figure(figsize=(10,5))
    plt.bar(unique_years, counts, color="#4472C4")
    plt.xlabel("Year")
    plt.ylabel("Number of earthquakes")
    plt.title("Annual frequency of earthquakes")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig("annual_count.png", dpi=300)
    plt.close()


def plot_annual_mean_mag(years, magnitudes):
    unique_years = np.unique(years)
    mean_mags = []
    for y in unique_years:
        mask = years == y
        mean_m = np.mean(magnitudes[mask])
        mean_mags.append(mean_m)
    plt.figure(figsize=(10,5))
    plt.plot(unique_years, mean_mags, marker="o", color="#ED7D31", linewidth=2)
    plt.xlabel("Year")
    plt.ylabel("Average magnitude")
    plt.title("Annual average earthquake magnitude")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("annual_mean_mag.png", dpi=300)
    plt.close()

# With all the above functions defined, we can now call them and get the result
if __name__ == "__main__":
    data = get_data()
    print(f"Loaded {count_earthquakes(data)} earthquakes")
    max_magnitude, max_location = get_maximum(data)
    print(f"The strongest earthquake was at {max_location} with magnitude {max_magnitude}")


# 绘图部分
    years_arr, mags_arr = extract_year_mag(data)
    plot_annual_count(years_arr, mags_arr)
    plot_annual_mean_mag(years_arr, mags_arr)
    print("Plots saved: annual_count.png , annual_mean_mag.png")
