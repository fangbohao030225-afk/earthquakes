import requests
import json
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timezone
import matplotlib.animation as animation

# --- Optional but recommended for coastlines ---
try:
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
except Exception:
    ccrs = None


# ----------------------------
# 1) Data loading & helper functions
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


def extract_quake_arrays(data):
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


# ----------------------------
# 2) Classwork12: Annual plots
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
# 3) Classwork13: map + histograms + animation
# ---------------------------------------
def _compute_circle_sizes(mags, min_size=10, max_size=200):
    if len(mags) == 0:
        return np.array([])
    m = np.array(mags, dtype=float)
    mmin, mmax = np.min(m), np.max(m)
    if mmax == mmin:
        return np.full_like(m, (min_size + max_size) / 2, dtype=float)
    t = (m - mmin) / (mmax - mmin)
    sizes = min_size + (t ** 1.7) * (max_size - min_size)
    return sizes


def _bin_edges(values, bin_deg):
    vmin, vmax = np.min(values), np.max(values)
    edges = np.arange(np.floor(vmin / bin_deg) * bin_deg,
                      np.ceil(vmax / bin_deg) * bin_deg + bin_deg,
                      bin_deg)
    return edges


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

    if ccrs is not None:
        ax_main = fig.add_subplot(gs[1, 0], projection=ccrs.PlateCarree())
        ax_main.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())
        ax_main.add_feature(cfeature.COASTLINE, lw=0.8, color="black")

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

    cbar = fig.colorbar(scat, ax=[ax_main, ax_top, ax_right], pad=0.02)
    cbar.set_label("Magnitude")

    if year is None:
        title = "Earthquakes (All years) - circle size ∝ magnitude"
    else:
        title = f"Earthquakes in {year} - circle size ∝ magnitude"
    ax_main.set_title(title)
    ax_main.set_xlabel("Longitude")
    ax_main.set_ylabel("Latitude")

    lon_edges = _bin_edges(lons, bin_deg)
    lat_edges = _bin_edges(lats, bin_deg)
    lon_bin_centers = 0.5 * (lon_edges[:-1] + lon_edges[1:])
    lat_bin_centers = 0.5 * (lat_edges[:-1] + lat_edges[1:])

    lon_counts, _ = np.histogram(sel_lons, bins=lon_edges)
    lat_counts, _ = np.histogram(sel_lats, bins=lat_edges)

    ax_top.bar(lon_bin_centers, lon_counts, width=bin_deg * 0.95, color="#4472C4", alpha=0.85)
    ax_top.set_ylabel("Count")
    ax_top.set_title(f"Longitude histogram (bin = {bin_deg}º)")
    ax_top.grid(axis="y", alpha=0.3)
    ax_top.set_xlim(lon_edges[0], lon_edges[-1])

    ax_right.barh(lat_bin_centers, lat_counts, height=bin_deg * 0.95, color="#ED7D31", alpha=0.85)
    ax_right.set_xlabel("Count")
    ax_right.set_title(f"Latitude histogram (bin = {bin_deg}º)")
    ax_right.grid(axis="x", alpha=0.3)
    ax_right.set_ylim(lat_edges[0], lat_edges[-1])

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close(fig)


def plot_lon_lat_with_histograms(
    data,
    year=None,
    animate=None,
    bin_deg=1.0,
    output_prefix="extra_plots",
    max_frames=None,
    interval_ms=200,
):
    lons, lats, mags, times_ms, years, dates_utc = extract_quake_arrays(data)
    lon_edges_all = _bin_edges(lons, bin_deg)
    lat_edges_all = _bin_edges(lats, bin_deg)
    lon_min, lon_max = lon_edges_all[0], lon_edges_all[-1]
    lat_min, lat_max = lat_edges_all[0], lat_edges_all[-1]

    def filter_mask_for_year(y):
        return years == y

    def filter_mask_for_date(d):
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

    if animate == "year":
        frame_keys = np.sort(np.unique(years)).tolist()
        frame_label_fn = lambda k: str(k)
        key_filter_fn = lambda k: filter_mask_for_year(k)
    elif animate == "day":
        unique_days = np.unique(dates_utc)
        frame_keys = sorted(unique_days.tolist())
        frame_label_fn = lambda d: str(d)
        key_filter_fn = lambda d: filter_mask_for_date(d)
    else:
        raise ValueError("animate must be None, 'year', or 'day'")

    if max_frames is not None and len(frame_keys) > max_frames:
        frame_keys = frame_keys[:max_frames]

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

    if ccrs is not None:
        ax_main = fig.add_subplot(gs[1, 0], projection=ccrs.PlateCarree())
        ax_main.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())
        ax_main.add_feature(cfeature.COASTLINE, lw=0.8, color="black")

    lon_edges = _bin_edges(lons, bin_deg)
    lat_edges = _bin_edges(lats, bin_deg)
    init_mask = key_filter_fn(frame_keys[0])
    init_lons, init_lats, init_mags = lons[init_mask], lats[init_mask], mags[init_mask]
    sizes = _compute_circle_sizes(init_mags)
    scat = ax_main.scatter(
        init_lons, init_lats,
        s=sizes, c=init_mags, cmap="viridis", alpha=0.55,
        transform=ccrs.PlateCarree() if ccrs is not None else None
    )
    cbar = fig.colorbar(scat, ax=[ax_main, ax_top, ax_right], pad=0.02)
    cbar.set_label("Magnitude")

    lon_bin_centers = 0.5 * (lon_edges[:-1] + lon_edges[1:])
    lat_bin_centers = 0.5 * (lat_edges[:-1] + lat_edges[1:])
    top_bars = ax_top.bar(lon_bin_centers, np.zeros(len(lon_bin_centers)), width=bin_deg * 0.95, color="#4472C4", alpha=0.8)
    right_bars = ax_right.barh(lat_bin_centers, np.zeros(len(lat_bin_centers)), height=bin_deg * 0.95, color="#ED7D31", alpha=0.8)

    ax_top.set_ylabel("Count")
    ax_right.set_xlabel("Count")
    ax_top.set_xlim(lon_edges[0], lon_edges[-1])
    ax_right.set_ylim(lat_edges[0], lat_edges[-1])

    title_text = ax_main.text(0.02, 0.98, "", transform=ax_main.transAxes, va="top", ha="left",
                              fontsize=12, bbox=dict(facecolor="white", alpha=0.7, edgecolor="none"))

    def update(frame_idx):
        key = frame_keys[frame_idx]
        mask = key_filter_fn(key)
        cur_lons = lons[mask]
        cur_lats = lats[mask]
        cur_mags = mags[mask]
        new_sizes = _compute_circle_sizes(cur_mags)
        scat.set_offsets(np.c_[cur_lons, cur_lats])
        scat.set_sizes(new_sizes)
        scat.set_array(cur_mags)
        lon_counts, _ = np.histogram(cur_lons, bins=lon_edges)
        lat_counts, _ = np.histogram(cur_lats, bins=lat_edges)
        for rect, h in zip(top_bars, lon_counts):
            rect.set_height(h)
        for rect, h in zip(right_bars, lat_counts):
            rect.set_width(h)
        title_text.set_text(f"Frame: {frame_label_fn(key)}")
        return (scat, top_bars, right_bars, title_text)

    ani = animation.FuncAnimation(fig, update, frames=len(frame_keys), interval=interval_ms, blit=False)
    out_path = f"{output_prefix}_animation_{animate}.gif"
    try:
        ani.save(out_path, writer="pillow", fps=max(2, int(1000 / interval_ms)))
    except Exception:
        out_path = f"{output_prefix}_animation_{animate}.mp4"
        ani.save(out_path, writer="ffmpeg", fps=max(2, int(1000 / interval_ms)))
    plt.close(fig)
    print(f"Saved animation: {out_path}")


# ----------------------------
# 4) Main entry
# ----------------------------
if __name__ == "__main__":
    data = get_data()
    print(f"Loaded {count_earthquakes(data)} earthquakes")
    max_magnitude, max_location = get_maximum(data)
    print(f"The strongest earthquake was at {max_location} with magnitude {max_magnitude}")

    # ========== Classwork12 两张图 ==========
    years_arr, mags_arr = extract_year_mag(data)
    plot_annual_count(years_arr, mags_arr)
    plot_annual_mean_mag(years_arr, mags_arr)
    print("Saved: annual_count.png , annual_mean_mag.png")

    # ========== Classwork13 静态地图+边缘直方图 ==========
    plot_lon_lat_with_histograms(data, year=None, animate=None, bin_deg=1.0)
    print("Saved: extra_plots_lon_lat.png")

    # ========== 动画（需要的时候取消注释运行） ==========
    # plot_lon_lat_with_histograms(data, animate="year", bin_deg=1.0)
    # plot_lon_lat_with_histograms(data, animate="day", bin_deg=1.0, max_frames=60)
