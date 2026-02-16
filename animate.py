#!/usr/bin/env python3
"""
Animate house construction over time from GPS coordinates.

Usage:
  python animate_houses.py --input houses.csv --output houses_animation.html --time-unit year

Options:
  --time-unit year|month|day   (default: year)
  --map-style open-street-map|carto-positron|carto-darkmatter|stamen-terrain
"""

import argparse
import pandas as pd
import plotly.express as px

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, help="CSV with columns lat, lon, date_built")
    p.add_argument("--output", default="houses_animation.html", help="Output HTML file")
    p.add_argument("--time-unit", default="year", choices=["year", "month", "day"],
                   help="Granularity for animation frames")
    p.add_argument("--map-style", default="open-street-map",
                   choices=["open-street-map", "carto-positron", "carto-darkmatter", "stamen-terrain"],
                   help="Basemap style (no API key needed)")
    return p.parse_args()

def add_time_bucket(df: pd.DataFrame, unit: str) -> pd.DataFrame:
    # Ensure datetime
    df["date_built"] = pd.to_datetime(df["date_built"], errors="coerce")
    df = df.dropna(subset=["date_built", "lat", "lon"]).copy()

    if unit == "year":
        df["time_bucket"] = df["date_built"].dt.year.astype(str)
        df["time_sort"] = df["date_built"].dt.year
    elif unit == "month":
        # 2020-03 style
        df["time_bucket"] = df["date_built"].dt.to_period("M").astype(str)
        df["time_sort"] = df["date_built"].dt.to_period("M").astype(str)
    else:  # day
        df["time_bucket"] = df["date_built"].dt.date.astype(str)
        df["time_sort"] = df["date_built"].dt.date.astype(str)

    # Make sure frames are ordered
    df = df.sort_values(["time_sort"])
    return df

def compute_map_center(df: pd.DataFrame):
    return dict(lat=float(df["lat"].median()), lon=float(df["lon"].median()))

def main():
    args = parse_args()
    df = pd.read_csv(args.input)

    required = {"lat", "lon", "date_built"}
    missing = required - set(df.columns)
    if missing:
        raise SystemExit(f"Missing required columns: {sorted(missing)}")

    df = add_time_bucket(df, args.time_unit)

    # If you want marker size to grow with time (cumulative effect), Plotly’s animation
    # shows only each frame’s points. We can make it cumulative by duplicating earlier points
    # into later frames.
    #
    # Cumulative build-out: for each time bucket, include all points built up to that bucket.
    buckets = df["time_bucket"].unique().tolist()
    cumulative_frames = []
    built_so_far = pd.DataFrame(columns=df.columns)

    for b in buckets:
        built_so_far = pd.concat([built_so_far, df[df["time_bucket"] == b]], ignore_index=True)
        temp = built_so_far.copy()
        temp["time_bucket"] = b  # label the frame
        cumulative_frames.append(temp)

    df_anim = pd.concat(cumulative_frames, ignore_index=True)

    center = compute_map_center(df_anim)

    # Hover text: include id if present
    hover_cols = []
    if "id" in df_anim.columns:
        hover_cols.append("id")
    hover_cols.append("date_built")

    fig = px.scatter_map(
        df_anim,
        lat="lat",
        lon="lon",
        animation_frame="time_bucket",
        hover_data=hover_cols,
        zoom=12,
        center=center,
        height=700,
    )

    fig.update_layout(
        map_style=args.map_style,
        margin=dict(l=10, r=10, t=40, b=10),
        title=f"Houses Built Over Time ({args.time_unit})",
    )

    # Make points more visible
    fig.update_traces(marker=dict(size=8, opacity=0.7))

    # Speed controls (optional tweak)
    # This affects the play button speed.
    fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 600
    fig.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = 150

    fig.write_html(args.output, include_plotlyjs="cdn")
    print(f"Wrote: {args.output}")

if __name__ == "__main__":
    main()
