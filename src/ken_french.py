"""Download and parse factor data from the Ken French Data Library.

Ken French publishes each dataset as a ZIP containing one CSV. The CSVs are
not clean tables: they start with a few lines of text (title, notes), then a
monthly returns block, and often an annual returns block at the bottom. All
returns are in **percent**, and missing values use the sentinels -99.99 / -999.
"""

from __future__ import annotations

import io
import zipfile
from urllib.request import urlopen

import pandas as pd

BASE_URL = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp"

# Each region needs two files: the 3-factor file (market/size/value + risk-free)
# and the standalone momentum file. Column layouts are identical across regions.
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

# Documented "missing data" markers in the Ken French files.
MISSING_VALUES = [-99.99, -999]


def download_csv_from_zip(filename: str) -> str:
    """Download a Ken French ZIP and return the text of the CSV inside it."""
    with urlopen(f"{BASE_URL}/{filename}", timeout=60) as response:
        archive = zipfile.ZipFile(io.BytesIO(response.read()))

    # Every archive holds exactly one CSV.
    csv_name = next(name for name in archive.namelist() if name.lower().endswith(".csv"))
    return archive.read(csv_name).decode("utf-8")


def parse_monthly_csv(text: str) -> pd.DataFrame:
    """Turn one Ken French CSV into a month-end-indexed DataFrame of returns.

    We keep only the monthly rows, which are the ones whose first field is a
    6-digit YYYYMM date (this naturally drops the header notes and the annual
    block, whose dates are 4 digits).
    """
    lines = text.splitlines()

    # The real header is the first line that starts with a comma, e.g. ",Mkt-RF,SMB,...".
    header_idx = next(i for i, line in enumerate(lines) if line.strip().startswith(","))
    columns = [name.strip() for name in lines[header_idx].split(",") if name.strip()]

    records = {}
    for line in lines[header_idx + 1 :]:
        fields = [field.strip() for field in line.split(",")]
        period = fields[0]
        if len(period) == 6 and period.isdigit():  # keep monthly rows only
            records[period] = fields[1 : 1 + len(columns)]

    frame = pd.DataFrame.from_dict(records, orient="index", columns=columns)
    frame = frame.apply(pd.to_numeric, errors="coerce")
    frame = frame.replace(MISSING_VALUES, pd.NA)

    # Index by the last calendar day of each month for clean time-series joins.
    frame.index = pd.to_datetime(frame.index, format="%Y%m") + pd.offsets.MonthEnd(0)
    frame.index.name = "date"
    return frame.sort_index()


def load_regional_factors(region_key: str) -> pd.DataFrame:
    """Load one region's market and momentum factors into a single DataFrame.

    Columns: Mkt-RF, SMB, HML, RF (from the 3-factor file), WML (momentum),
    plus Mkt = Mkt-RF + RF (the total market return, used for charts).
    """
    region = REGIONS[region_key]

    factors = parse_monthly_csv(download_csv_from_zip(region["factors_zip"]))
    momentum = parse_monthly_csv(download_csv_from_zip(region["momentum_zip"]))

    combined = factors.join(momentum, how="inner")
    combined["Mkt"] = combined["Mkt-RF"] + combined["RF"]
    return combined


def load_all_regions() -> dict[str, pd.DataFrame]:
    """Load every region in REGIONS, keyed by region key."""
    return {region_key: load_regional_factors(region_key) for region_key in REGIONS}
