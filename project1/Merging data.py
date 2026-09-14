"""
Merge the three project data sources into one analysis-ready dataset:
  - acs_income_education.csv  (state, year, median_hh_income, pct_bachelors_or_higher)
  - turnout_clean.csv         (state, year, turnout_rate)
  - voter_id_stringency.csv   (state_name, year, id_stringency_tier, ...)

Run this after all three source scripts have been run and their CSVs
exist in the same folder.
"""

import pandas as pd

def main():
    acs = pd.read_csv("acs_income_education.csv", dtype={"state": str})
    turnout = pd.read_csv("turnout_clean.csv", dtype={"state": str})
    stringency = pd.read_csv("voter_id_stringency.csv")

    # ACS's FIPS codes come back from the Census API without zero-padding
    # in some cases -- normalize to 2-digit strings so joins line up.
    acs["state"] = acs["state"].str.zfill(2)
    turnout["state"] = turnout["state"].str.zfill(2)

    # Step 1: join ACS + turnout on FIPS code + year
    merged = pd.merge(
        acs,
        turnout[["state", "year", "turnout_rate"]],
        on=["state", "year"],
        how="inner",
    )

    before = len(merged)
    print(f"After ACS + turnout join: {before} rows")

    # Step 2: join in voter ID stringency on state name + year
    # (state names must match exactly -- e.g. "state_name" from ACS's
    # NAME field vs. the hand-typed names in voter_id_stringency.csv)
    merged = pd.merge(
        merged,
        stringency[["state_name", "year", "id_stringency_tier", "tier_label", "verified"]],
        on=["state_name", "year"],
        how="left",
    )

    after = len(merged)
    unmatched = merged[merged["id_stringency_tier"].isna()]
    if len(unmatched):
        print(f"WARNING: {len(unmatched)} rows have no matching stringency data:")
        print(unmatched[["state_name", "year"]].to_string(index=False))
    else:
        print(f"All {after} rows matched to a stringency tier.")

    # Final column order for readability
    cols = [
        "state_name", "state", "year",
        "turnout_rate", "id_stringency_tier", "tier_label", "verified",
        "median_hh_income", "pct_bachelors_or_higher",
    ]
    merged = merged[cols].sort_values(["state_name", "year"]).reset_index(drop=True)

    merged.to_csv("analysis_dataset.csv", index=False)
    print(f"\nSaved {len(merged)} rows to analysis_dataset.csv")
    print(merged.head(10))

if __name__ == "__main__":
    main()