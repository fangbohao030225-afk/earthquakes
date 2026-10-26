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

# Extra plots for earthquake dataset  
import json  
import requests  
import numpy as np  
import matplotlib.pyplot as plt  
from datetime import datetime, timezone  

# --- Optional but recommended for coastlines ---  
try:  
    import cartopy.crs as ccrs  
except Exception:  
    ccrs = None  


# ----------------------------  
# 1) Data loading & helpers  
# ----------------------------  
def get_data():  
    response = requests.get(  
        "http://earthquake.usgs.gov/fdsnws/event/1/query.geojson",  
        params={  
            "starttime": "2000-01-01",  
            "maxlatitude": "58.723",  
            "minlatitude": "50.008",  
            "maxlongitude": "1.67",  
            "minlongitude": "-9.756",  
            "minmagnitude": "1",  
            "endtime": "2018-10-11",  
            "orderby": "time-asc",  
        },  
    )  
    return json.loads(response.text)  


def count_earthquakes(data):  
    return len(data["features"])  


def get_magnitude(earthquake):  
    return earthquake["properties"]["mag"]  


def get_location(earthquake):  
    # coordinates: [longitude, latitude, depth]  
    coordinates = earthquake["geometry"]["coordinates"]  
    lat = coordinates[1]  
    lon = coordinates[0]  
    return lat, lon  


def get_maximum(data):  
    max_mag = -1.0  
    max_pos = None  
    for quake in data["features"]:  
        mag = get_magnitude(quake)  
        # mag could be None  
        if mag is None:  
            continue  
        if mag > max_mag:  
            max_mag = mag  
            max_pos = get_location(quake)  
    return max_mag, max_pos  


def extract_year_mag(data):  
    years = []  
    magnitudes = []  
    for quake in data["features"]:  
        time_ms = quake["properties"]["time"]  
        time_sec = time_ms / 1000  
        dt = datetime.fromtimestamp(time_sec, tz=timezone.utc)  
        year = dt.year  

        mag = get_magnitude(quake)  
        if mag is None:  
            continue  

        years.append(year)  
        magnitudes.append(mag)  
    return np.array(years), np.array(magnitudes)  


# ----------------------------  
# 2) Annual plots (your existing)  
# ----------------------------  
def plot_annual_count(years, magnitudes):  
    unique_years, counts = np.unique(years, return_counts=True)  
    plt.figure(figsize=(10, 5))  
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
        mean_mags.append(np.mean(magnitudes[mask]))  

    plt.figure(figsize=(10, 5))  
    plt.plot(unique_years, mean_mags, marker="o", color="#ED7D31", linewidth=2)  
    plt.xlabel("Year")  
    plt.ylabel("Average magnitude")  
    plt.title("Annual average earthquake magnitude")  
    plt.grid(alpha=0.3)  
    plt.tight_layout()  
    plt.savefig("annual_mean_mag.png", dpi=300)  
    plt.close()  


# ---------------------------------------  
# 3) Extra plots: map + histograms + anim  
# ---------------------------------------  
def extract_quake_arrays(data):  
    """  
    Returns:  
      lons, lats, mags, times_ms, years, dates_utc  
    """  
    lons, lats, mags, times_ms, years, dates_utc = [], [], [], [], [], []  

    for quake in data["features"]:  
        mag = get_magnitude(quake)  
        if mag is None:  
            continue  

        lat, lon = get_location(quake)  
        time_ms = quake["properties"]["time"]  

        dt = datetime.fromtimestamp(time_ms / 1000, tz=timezone.utc)  
        lons.append(lon)  
        lats.append(lat)  
        mags.append(mag)  
        times_ms.append(time_ms)  
        years.append(dt.year)  
        dates_utc.append(dt.date())  

    return (  
        np.array(lons, dtype=float),  
        np.array(lats, dtype=float),  
        np.array(mags, dtype=float),  
        np.array(times_ms, dtype=float),  
        np.array(years, dtype=int),  
        np.array(dates_utc, dtype=object),  
    )  


def _compute_circle_sizes(mags, min_size=10, max_size=200):  
    """  
    Scale marker sizes with magnitude.  
    """  
    if len(mags) == 0:  
        return np.array([])  
    m = np.array(mags, dtype=float)  
    mmin, mmax = np.min(m), np.max(m)  
    if mmax == mmin:  
        return np.full_like(m, (min_size + max_size) / 2, dtype=float)  

    # Normalize to [0, 1]  
    t = (m - mmin) / (mmax - mmin)  
    # Smooth-ish scaling  
    sizes = min_size + (t ** 1.7) * (max_size - min_size)  
    return sizes  


def _bin_edges(values, bin_deg):  
    vmin, vmax = np.min(values), np.max(values)  
    # include right edge  
    edges = np.arange(np.floor(vmin / bin_deg) * bin_deg, np.ceil(vmax / bin_deg) * bin_deg + bin_deg, bin_deg)  
    return edges  


def plot_lon_lat_with_histograms(  
    data,  
    year=None,  
    animate=None,          # None | "year" | "day"  
    bin_deg=1.0,  
    output_prefix="extra_plots",  
    max_frames=None,      # safety: for day animation you can cap frames  
    interval_ms=200,  
):  
    """  
    Requirements:  
    - longitude-latitude plot with circles scaled by magnitude  
    - coastlines background (cartopy) if available  
    - optional year filter  
    - optional animation year/day  
    - histograms on the top (lon) and right (lat) sides with binned range bin_deg  
    """  
    lons, lats, mags, times_ms, years, dates_utc = extract_quake_arrays(data)  

    # Base extent for map (fixed so frames don't "jump")  
    lon_edges_all = _bin_edges(lons, bin_deg)  
    lat_edges_all = _bin_edges(lats, bin_deg)  
    lon_min, lon_max = lon_edges_all[0], lon_edges_all[-1]  
    lat_min, lat_max = lat_edges_all[0], lat_edges_all[-1]  

    def filter_mask_for_year(y):  
        return years == y  

    def filter_mask_for_date(d):  
        # dates_utc is object array of datetime.date  
        return dates_utc == d  

    if animate is None:  
        mask = np.ones_like(lons, dtype=bool)  
        if year is not None:  
            mask = filter_mask_for_year(year)  

        plot_once(  
            lons, lats, mags, mask,  
            lon_min, lon_max, lat_min, lat_max,  
            bin_deg, year=year,  
            output_path=f"{output_prefix}_lon_lat.png"  
        )  
        return  

    # Animation: build frames  
    if animate == "year":  
        frame_keys = np.sort(np.unique(years)).tolist()  
        frame_label_fn = lambda k: str(k)  
        key_filter_fn = lambda k: filter_mask_for_year(k)  
    elif animate == "day":  
        # Keep only days with earthquakes to avoid thousands of empty frames  
        unique_days = np.unique(dates_utc)  
        # Sort days  
        frame_keys = sorted(unique_days.tolist())  
        frame_label_fn = lambda d: str(d)  # YYYY-MM-DD  
        key_filter_fn = lambda d: filter_mask_for_date(d)  
    else:  
        raise ValueError("animate must be None, 'year', or 'day'")  

    if max_frames is not None and len(frame_keys) > max_frames:  
        frame_keys = frame_keys[:max_frames]  

    # Create animation  
    if ccrs is None:  
        print("Warning: cartopy not available -> coastlines won't be shown in animation.")  

    import matplotlib.animation as animation  

    # Layout: top histogram + main map + right histogram  
    fig = plt.figure(figsize=(12, 8))  
    gs = fig.add_gridspec(  
        2, 2,  
        width_ratios=[4, 1.6],  # main, right histogram  
        height_ratios=[1.2, 4],  # top histogram, main  
        wspace=0.05, hspace=0.05  
    )  

    ax_top = fig.add_subplot(gs[0, 0])  
    ax_main = fig.add_subplot(gs[1, 0])  

    ax_right = fig.add_subplot(gs[1, 1])  

    # Coastlines-capable axis  
    if ccrs is not None:  
        ax_main = fig.add_subplot(gs[1, 0], projection=ccrs.PlateCarree())  

    # Prepare bins (fixed so histogram axes stay consistent)  
    lon_edges = _bin_edges(lons, bin_deg)  
    lat_edges = _bin_edges(lats, bin_deg)  

    # Initial data  
    init_mask = key_filter_fn(frame_keys[0])  
    init_lons, init_lats, init_mags = lons[init_mask], lats[init_mask], mags[init_mask]  

    # Initial scatter  
    sizes = _compute_circle_sizes(init_mags)  
    scat = ax_main.scatter(  
        init_lons, init_lats,  
        s=sizes,  
        c=init_mags,  
        cmap="viridis",  
        alpha=0.55,  
        linewidths=0.2,  
        edgecolors="none",  
        transform=ccrs.PlateCarree() if ccrs is not None else None  
    )  

    # Colorbar  
    cbar = fig.colorbar(scat, ax=[ax_main, ax_top, ax_right], pad=0.02)  
    cbar.set_label("Magnitude")  

    # Static map styling  
    if ccrs is not None:  
        ax_main.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())  
        ax_main.coastlines(resolution="110m", linewidth=0.8, color="black")  
    ax_main.set_xlabel("Longitude")  
    ax_main.set_ylabel("Latitude")  
    ax_main.set_title(f"Earthquakes (circle size ∝ magnitude) - {animate}")  

    # Histograms containers  
    lon_bin_centers = 0.5 * (lon_edges[:-1] + lon_edges[1:])  
    lat_bin_centers = 0.5 * (lat_edges[:-1] + lat_edges[1:])  

    top_bars = ax_top.bar(lon_bin_centers, np.zeros(len(lon_bin_centers)), width=bin_deg * 0.95, color="#4472C4", alpha=0.8)  
    right_bars = ax_right.barh(lat_bin_centers, np.zeros(len(lat_bin_centers)), height=bin_deg * 0.95, color="#ED7D31", alpha=0.8)  

    # Histogram axis labels  
    ax_top.set_ylabel("Count")  
    ax_top.set_xlabel("Longitude (binned)")  
    ax_top.set_title(f"Longitude histogram (bin = {bin_deg}º)")  
    ax_top.grid(axis="y", alpha=0.3)  
    ax_top.tick_params(axis="x", labelrotation=0)  

    ax_right.set_xlabel("Count")  
    ax_right.set_ylabel("Latitude (binned)")  
    ax_right.set_title(f"Latitude histogram (bin = {bin_deg}º)")  
    ax_right.grid(axis="x", alpha=0.3)  

    # Reduce clutter for hist axes  
    ax_top.set_xlim(lon_edges[0], lon_edges[-1])  
    ax_right.set_ylim(lat_edges[0], lat_edges[-1])  

    # Frame title text  
    title_text = ax_main.text(  
        0.02, 0.98, "",  
        transform=ax_main.transAxes if ccrs is None else ax_main.transAxes,  
        va="top", ha="left",  
        fontsize=12,  
        bbox=dict(facecolor="white", alpha=0.7, edgecolor="none")  
    )  

    def update(frame_idx):  
        key = frame_keys[frame_idx]  
        mask = key_filter_fn(key)  

        cur_lons = lons[mask]  
        cur_lats = lats[mask]  
        cur_mags = mags[mask]  

        # Update scatter sizes and colors  
        new_sizes = _compute_circle_sizes(cur_mags)  
        # matplotlib scatter doesn't allow changing s/colors arrays trivially across all versions,  
        # but set_offsets + set_sizes + set_array works.  
        scat.set_offsets(np.c_[cur_lons, cur_lats])  
        scat.set_sizes(new_sizes)  
        scat.set_array(cur_mags)  

        # Update histograms  
        lon_counts, _ = np.histogram(cur_lons, bins=lon_edges)  
        lat_counts, _ = np.histogram(cur_lats, bins=lat_edges)  

        for rect, h in zip(top_bars, lon_counts):  
            rect.set_height(h)  
        for rect, h in zip(right_bars, lat_counts):  
            rect.set_width(h)  

        title_text.set_text(f"Frame: {frame_label_fn(key)}")  
        return (scat, top_bars, right_bars, title_text)  

    ani = animation.FuncAnimation(  
        fig,  
        update,  
        frames=len(frame_keys),  
        interval=interval_ms,  
        blit=False  
    )  

    # Save animation  
    out_path = f"{output_prefix}_animation_{animate}.gif"  
    try:  
        ani.save(out_path, writer="pillow", fps=max(2, int(1000 / interval_ms)))  
    except Exception:  
        # Fallback: try mp4 via ffmpeg  
        out_path = f"{output_prefix}_animation_{animate}.mp4"  
        ani.save(out_path, writer="ffmpeg", fps=max(2, int(1000 / interval_ms)))  

    plt.close(fig)  
    print(f"Saved animation: {out_path}")  


def plot_once(lons, lats, mags, mask, lon_min, lon_max, lat_min, lat_max, bin_deg, year=None, output_path="extra.png"):  
    sel_lons = lons[mask]  
    sel_lats = lats[mask]  
    sel_mags = mags[mask]  

    fig = plt.figure(figsize=(12, 8))  
    gs = fig.add_gridspec(  
        2, 2,  
        width_ratios=[4, 1.6],  
        height_ratios=[1.2, 4],  
        wspace=0.05, hspace=0.05  
    )  

    ax_top = fig.add_subplot(gs[0, 0])  
    ax_main = fig.add_subplot(gs[1, 0])  
    ax_right = fig.add_subplot(gs[1, 1])  

    # If cartopy exists, recreate main axis as map projection  
    if ccrs is not None:  
        ax_main = fig.add_subplot(gs[1, 0], projection=ccrs.PlateCarree())  
        ax_main.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())  
        ax_main.coastlines(resolution="110m", linewidth=0.8, color="black")  

    # Scatter  
    sizes = _compute_circle_sizes(sel_mags)  
    scat = ax_main.scatter(  
        sel_lons, sel_lats,  
        s=sizes,  
        c=sel_mags,  
        cmap="viridis",  
        alpha=0.55,  
        linewidths=0.2,  
        edgecolors="none",  
        transform=ccrs.PlateCarree() if ccrs is not None else None  
    )  

    # Colorbar  
    cbar = fig.colorbar(scat, ax=[ax_main, ax_top, ax_right], pad=0.02)  
    cbar.set_label("Magnitude")  

    # Titles/labels  
    if year is None:  
        title = "Earthquakes (All years) - circle size ∝ magnitude"  
    else:  
        title = f"Earthquakes in {year} - circle size ∝ magnitude"  

    ax_main.set_title(title)  
    ax_main.set_xlabel("Longitude")  
    ax_main.set_ylabel("Latitude")  

    # Fixed histogram bins (based on global data ranges)  
    lon_edges = _bin_edges(lons, bin_deg)  
    lat_edges = _bin_edges(lats, bin_deg)  

    lon_bin_centers = 0.5 * (lon_edges[:-1] + lon_edges[1:])  
    lat_bin_centers = 0.5 * (lat_edges[:-1] + lat_edges[1:])  

    lon_counts, _ = np.histogram(sel_lons, bins=lon_edges)  
    lat_counts, _ = np.histogram(sel_lats, bins=lat_edges)  

    # Top histogram: counts by longitude  
    ax_top.bar(lon_bin_centers, lon_counts, width=bin_deg * 0.95, color="#4472C4", alpha=0.85)  
    ax_top.set_ylabel("Count")  
    ax_top.set_xlabel("Longitude (binned)")  
    ax_top.set_title(f"Longitude histogram (bin = {bin_deg}º)")  
    ax_top.grid(axis="y", alpha=0.3)  
    ax_top.set_xlim(lon_edges[0], lon_edges[-1])  

    # Right histogram: counts by latitude  
    ax_right.barh(lat_bin_centers, lat_counts, height=bin_deg * 0.95, color="#ED7D31", alpha=0.85)  
    ax_right.set_xlabel("Count")  
    ax_right.set_ylabel("Latitude (binned)")  
    ax_right.set_title(f"Latitude histogram (bin = {bin_deg}º)")  
    ax_right.grid(axis="x", alpha=0.3)  
    ax_right.set_ylim(lat_edges[0], lat_edges[-1])  

    plt.tight_layout()  
    plt.savefig(output_path, dpi=300)  
    plt.close(fig)  


# ----------------------------  
# 4) Main: run everything  
# ----------------------------  
if __name__ == "__main__":  
    data = get_data()  
    print(f"Loaded {count_earthquakes(data)} earthquakes")  

    max_magnitude, max_location = get_maximum(data)  
   