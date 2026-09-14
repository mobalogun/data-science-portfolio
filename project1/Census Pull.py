"""
Pull state-level ACS 5-Year Estimates (income + education) for the
voter ID / turnout project.

ACS5 vintage note: the `year` param is the END year of the 5-year window.
  year=2012 -> 2008-2012 ACS5 (aligns with the 2012 election)
  year=2020 -> 2016-2020 ACS5 (aligns with the 2020 election)

Usage:
    export CENSUS_API_KEY="your_key_here"
    python census_pull.py
"""

import os
import requests
import pandas as pd

API_KEY = os.environ.get("CENSUS_API_KEY", "eed7087f66df252ec16fc3c56c31662648470177")

# Election years mapped to their matching ACS5 vintage (end year of window)
YEARS = [2012, 2020]  # add 2014, 2016, 2018 later if time allows

def pull_income(year: int) -> pd.DataFrame:
    """Median household income, B19013_001E, from the detail tables API."""
    url = f"https://api.census.gov/data/{year}/acs/acs5"
    params = {
        "get": "NAME,B19013_001E",
        "for": "state:*",
        "key": API_KEY,
    }
    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()
    df = pd.DataFrame(data[1:], columns=data[0])
    df = df.rename(columns={"B19013_001E": "median_hh_income"})
    df["median_hh_income"] = pd.to_numeric(df["median_hh_income"], errors="coerce")
    df["year"] = year
    return df

def find_bachelors_variable(year: int) -> str:
    """
    DP02's variable numbering shifts between ACS vintages (e.g. DP02_0067PE
    in some years, DP02_0068PE in others), so instead of hardcoding a code,
    look up the variable list for this year and match on the label text.
    """
    url = f"https://api.census.gov/data/{year}/acs/acs5/profile/variables.json"
    r = requests.get(url)
    r.raise_for_status()
    variables = r.json()["variables"]

    for code, meta in variables.items():
        label = meta.get("label", "")
        # Looking for the PERCENT estimate (not margin of error, not annotation)
        # of "...Bachelor's degree or higher", e.g.
        # "Percent!!EDUCATIONAL ATTAINMENT!!...!!Bachelor's degree or higher"
        if (
            code.endswith("PE")
            and "bachelor's degree or higher" in label.lower()
            and "percent" in label.lower()
        ):
            return code

    raise ValueError(
        f"Could not find a 'percent bachelor's degree or higher' variable "
        f"for {year}. Check {url} manually."
    )


def pull_education(year: int) -> pd.DataFrame:
    """% bachelor's degree or higher, looked up dynamically per vintage."""
    var_code = find_bachelors_variable(year)
    print(f"{year}: using variable {var_code} for pct bachelor's or higher")

    url = f"https://api.census.gov/data/{year}/acs/acs5/profile"
    params = {
        "get": f"NAME,{var_code}",
        "for": "state:*",
        "key": API_KEY,
    }
    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()
    df = pd.DataFrame(data[1:], columns=data[0])
    df = df.rename(columns={var_code: "pct_bachelors_or_higher"})
    df["pct_bachelors_or_higher"] = pd.to_numeric(
        df["pct_bachelors_or_higher"], errors="coerce"
    )
    df["year"] = year
    return df

def main():
    income_frames = [pull_income(y) for y in YEARS]
    edu_frames = [pull_education(y) for y in YEARS]

    income_df = pd.concat(income_frames, ignore_index=True)
    edu_df = pd.concat(edu_frames, ignore_index=True)

    merged = pd.merge(
        income_df,
        edu_df,
        on=["NAME", "state", "year"],
        how="outer",
    )

    merged = merged.rename(columns={"NAME": "state_name"})
    merged.to_csv("acs_income_education.csv", index=False)
    print(f"Saved {len(merged)} rows to acs_income_education.csv")
    print(merged.head())

if __name__ == "__main__":
    main()