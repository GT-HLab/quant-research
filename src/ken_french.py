"""Utilities for downloading and parsing Ken French Data Library CSV files."""

from __future__ import annotations

import io
import zipfile
from urllib.request import urlopen

import pandas as pd

BASE_URL = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp"

REGIONS = {
    "north_america": {
        "label": "North America",
        "factors_zip": "North_America_3_Factors_CSV.zip",
        "momentum_zip": "North_America_Mom_Factor_CSV.zip",
    },
    "europe": {
        "label": "Europe",
        "factors_zip": "Europe_3_Factors_CSV.zip",
        "momentum_zip": "Europe_Mom_Factor_CSV.zip",
    },
    "asia_ex_japan": {
        "label": "Asia ex Japan",
        "factors_zip": "Asia_Pacific_ex_Japan_3_Factors_CSV.zip",
        "momentum_zip": "Asia_Pacific_ex_Japan_Mom_Factor_CSV.zip",
    },
    "japan": {
        "label": "Japan",
        "factors_zip": "Japan_3_Factors_CSV.zip",
        "momentum_zip": "Japan_Mom_Factor_CSV.zip",
    },
}


def download_zip_csv(filename: str) -> str:
    """Download a Ken French ZIP archive and return the CSV text inside."""
    url = f"{BASE_URL}/{filename}"
    with urlopen(url, timeout=60) as response:
        payload = response.read()

    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        csv_names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
        if not csv_names:
            raise ValueError(f"No CSV file found in archive: {filename}")
        return archive.read(csv_names[0]).decode("utf-8")


def _find_header_line(lines: list[str]) -> int:
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(",") and any(token.strip() for token in stripped.split(",")[1:]):
            return idx
    raise ValueError("Could not locate CSV header row.")


def parse_ken_french_csv(text: str) -> pd.DataFrame:
    """Parse a Ken French monthly CSV file into a date-indexed DataFrame."""
    lines = text.splitlines()
    header_idx = _find_header_line(lines)
    header = [col.strip() for col in lines[header_idx].split(",") if col.strip()]

    rows: list[list[str]] = []
    for line in lines[header_idx + 1 :]:
        stripped = line.strip()
        if not stripped:
            continue

        parts = [part.strip() for part in line.split(",")]
        date_token = parts[0]
        if len(date_token) != 6 or not date_token.isdigit():
            continue

        values = parts[1 : 1 + len(header)]
        if len(values) < len(header):
            continue

        rows.append([date_token, *values])

    frame = pd.DataFrame(rows, columns=["period", *header])
    frame[header] = frame[header].apply(pd.to_numeric, errors="coerce")
    frame.index = pd.to_datetime(frame["period"], format="%Y%m") + pd.offsets.MonthEnd(0)
    frame.index.name = "date"
    return frame.drop(columns=["period"]).sort_index()


def load_regional_factors(region_key: str) -> pd.DataFrame:
    """Load market and momentum factors for a region into one DataFrame."""
    if region_key not in REGIONS:
        raise KeyError(f"Unknown region: {region_key}")

    region = REGIONS[region_key]
    factors = parse_ken_french_csv(download_zip_csv(region["factors_zip"]))
    momentum = parse_ken_french_csv(download_zip_csv(region["momentum_zip"]))

    combined = factors.join(momentum, how="inner")
    combined.columns = ["Mkt-RF", "SMB", "HML", "RF", "WML"]
    combined["Mkt"] = combined["Mkt-RF"] + combined["RF"]
    combined = combined[["Mkt-RF", "RF", "Mkt", "SMB", "HML", "WML"]]
    combined.attrs["region"] = region["label"]
    return combined


def build_factor_panel(
    regional_factors: dict[str, pd.DataFrame] | None = None,
    factors: tuple[str, ...] = ("Mkt", "WML"),
) -> pd.DataFrame:
    """Build one date-indexed DataFrame with one column per region/factor pair."""
    if regional_factors is None:
        regional_factors = {key: load_regional_factors(key) for key in REGIONS}

    series: dict[str, pd.Series] = {}
    for region_key, meta in REGIONS.items():
        region_df = regional_factors[region_key]
        for factor in factors:
            column_name = f"{meta['label']}_{factor}"
            series[column_name] = region_df[factor]

    panel = pd.DataFrame(series)
    panel.index.name = "date"
    return panel.sort_index()
