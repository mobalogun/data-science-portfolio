"""
Builds the voter ID stringency table (3-tier, simplified per project scope).

TIER SCHEME:
  0 = No ID required to vote at the polls
  1 = ID requested/required, but a voter without one can still cast a
      ballot that counts without further action (affidavit, poll worker
      attestation, non-strict non-photo document, etc.)
  2 = Strict requirement — voter without accepted ID casts a provisional
      ballot and must take an extra step after Election Day for it to count

IMPORTANT: 'verified' column marks entries backed by a specific historical
source (see notes). Anything 'verified'=False is a DEFAULT based on
today's NCSL classification and may be WRONG for that specific year --
voter ID law is one of the most litigated, frequently-changed areas of
election law. Check the flagged ones before using this in your writeup.

Known trouble spots already handled below:
  - TX, WI (2012): strict photo ID laws passed but BLOCKED BY COURTS,
    did not apply to the actual 2012 election -> coded as prior tier 1
  - PA (2012): strict law passed but blocked before election -> tier 1
  - NC (2020): 2018 photo ID law blocked by courts through the 2020
    general election -> tier 0, NOT today's tier 2
  - AR, ID, MO, MT, NE, OH, WY: enacted STRICTER id laws AFTER 2020
    (per NCSL/NBC reporting) -> today's classification would overstate
    their 2020 stringency. Coded here as tier 1 default, but verify.
"""

import pandas as pd

# name -> (2012_tier, 2012_verified, 2012_note, 2020_tier, 2020_verified, 2020_note)
DATA = {
    # --- Fully verified 2012 entries (Ballotpedia "Voting in the 2012
    # general elections") ---
    "California":       (0, True,  "No ID required (Ballotpedia 2012)", 0, False, "Default: current NCSL 'no document' bucket"),
    "Illinois":         (0, True,  "No ID required (Ballotpedia 2012)", 0, False, "Default: current NCSL 'no document' bucket"),
    "Maine":            (0, True,  "No ID required (Ballotpedia 2012)", 0, False, "Default: current NCSL 'no document' bucket"),
    "Massachusetts":    (0, True,  "No ID required (Ballotpedia 2012)", 0, False, "Default: current NCSL 'no document' bucket"),
    "Nevada":           (0, True,  "No ID required (Ballotpedia 2012)", 0, False, "Default: current NCSL 'no document' bucket"),
    "New Hampshire":    (0, True,  "Law passed 2012 but effective date pushed to 2013", 1, False, "Default: current NCSL non-strict bucket"),
    "North Carolina":   (0, True,  "No ID required (Ballotpedia 2012)", 0, True, "2018 law blocked by courts through 2020 general election"),
    "Maryland":         (1, True,  "Select voters required ID (Ballotpedia 2012)", 0, False, "Default: current NCSL 'no document' bucket"),
    "Nebraska":         (1, True,  "Select voters required ID (Ballotpedia 2012)", 1, False, "NCSL: enacted stricter law after 2020, verify pre-2020 status"),
    "Pennsylvania":     (1, True,  "Strict law passed but blocked by courts before election", 0, False, "Default: current NCSL 'no document' bucket"),
    "Connecticut":      (1, True,  "Select voters required ID (Ballotpedia 2012)", 1, False, "Default: current NCSL non-strict bucket"),
    "New Jersey":       (1, True,  "Select voters required ID (Ballotpedia 2012)", 0, False, "Default: current NCSL 'no document' bucket"),
    "Iowa":             (1, True,  "Select voters required ID (Ballotpedia 2012)", 1, False, "Default: current NCSL non-strict bucket"),
    "Minnesota":        (1, True,  "Select voters required ID (Ballotpedia 2012)", 0, False, "Default: current NCSL 'no document' bucket"),
    "Texas":            (1, True,  "Strict photo law blocked by courts for 2012 election", 1, False, "Default: current NCSL non-strict photo bucket"),
    "Wisconsin":        (1, True,  "Strict photo law blocked by courts for 2012 election", 2, True, "Strict law finally implemented starting 2016, in effect by 2020"),
    "Georgia":          (2, True,  "Strict photo ID in effect since 2008 (Crawford v. Marion)", 2, True, "Same strict law remained in effect"),
    "Indiana":          (2, True,  "Strict photo ID in effect since 2008 (Crawford v. Marion)", 2, True, "Same strict law remained in effect"),
    "Kansas":           (2, True,  "Strict photo ID law took effect Jan 2012", 2, True, "Same strict law remained in effect"),
    "Tennessee":        (2, True,  "Strict photo ID law took effect 2012", 2, True, "Same strict law remained in effect"),

    # --- Remaining states: DEFAULT to current NCSL classification for
    # BOTH years -- these need your verification, especially any state
    # you know changed its law between 2012 and 2020 ---
    "Alabama":          (1, False, "Default: current classification", 1, False, "Default: current classification (AL law passed 2011, delayed to 2014 for preclearance -- verify 2012 status)"),
    "Alaska":           (1, False, "Default: current classification", 1, False, "Default: current classification"),
    "Arizona":          (2, False, "Default: current classification", 2, False, "Default: current classification"),
    "Arkansas":         (1, False, "Default: current classification", 1, False, "NCSL: enacted stricter law after 2020, verify pre-2020 status"),
    "Colorado":         (1, False, "Default: current classification", 1, False, "Default: current classification"),
    "Delaware":         (1, False, "Default: current classification", 1, False, "Default: current classification"),
    "Florida":          (1, False, "Default: current classification", 1, False, "Default: current classification"),
    "Hawaii":           (1, False, "Default: current classification", 1, False, "Default: current classification"),
    "Idaho":            (1, False, "Default: current classification", 1, False, "NCSL: enacted stricter law after 2020, verify pre-2020 status"),
    "Kentucky":         (1, False, "Default: current classification", 1, False, "KY moved to strict photo ID via 2021 law -- likely lower tier in 2012/2020, verify"),
    "Louisiana":        (1, False, "Default: current classification", 1, False, "Default: current classification"),
    "Michigan":         (1, False, "Default: current classification", 1, False, "Default: current classification"),
    "Mississippi":      (2, False, "Default: current classification", 2, False, "MS photo ID law approved 2011, implementation delayed to 2014 -- verify 2012 status"),
    "Missouri":         (1, False, "Default: current classification", 1, False, "NCSL: enacted stricter law after 2020, verify pre-2020 status"),
    "Montana":          (1, False, "Default: current classification", 1, False, "NCSL: enacted stricter law after 2020, verify pre-2020 status"),
    "New Mexico":       (0, False, "Default: current classification", 0, False, "Default: current classification"),
    "New York":         (0, False, "Default: current classification", 0, False, "Default: current classification"),
    "North Dakota":     (2, False, "Default: current classification", 2, False, "Default: current classification"),
    "Ohio":             (1, False, "Default: current classification", 1, False, "NCSL: enacted stricter law after 2020, verify pre-2020 status"),
    "Oklahoma":         (1, False, "Default: current classification", 1, False, "Default: current classification"),
    "Oregon":           (0, False, "Default: current classification", 0, False, "Default: current classification"),
    "Rhode Island":     (1, False, "Default: current classification", 1, False, "RI photo ID law took effect Jan 2012, verify if fully phased in for Nov 2012"),
    "South Carolina":   (1, False, "Default: current classification", 1, False, "SC 2011 law blocked by DOJ under Section 5, implemented 2013 -- verify 2012 status"),
    "South Dakota":     (1, False, "Default: current classification", 1, False, "Default: current classification"),
    "Utah":             (1, False, "Default: current classification", 1, False, "Default: current classification"),
    "Vermont":          (0, False, "Default: current classification", 0, False, "Default: current classification"),
    "Virginia":         (1, False, "Default: current classification", 2, False, "VA moved from non-strict to strict photo ID starting 2014 -- verify"),
    "Washington":       (1, False, "Default: current classification", 1, False, "Default: current classification"),
    "West Virginia":    (1, False, "Default: current classification", 1, False, "Default: current classification"),
    "Wyoming":          (2, False, "Default: current classification", 1, False, "NCSL: enacted stricter law after 2020, verify pre-2020 status"),
    "District of Columbia": (0, False, "Default: current classification", 0, False, "Default: current classification"),
}

TIER_LABELS = {0: "No ID required", 1: "ID requested/non-strict", 2: "Strict ID required"}


def build_table() -> pd.DataFrame:
    rows = []
    for state, (t12, v12, n12, t20, v20, n20) in DATA.items():
        rows.append({"state_name": state, "year": 2012, "id_stringency_tier": t12,
                     "tier_label": TIER_LABELS[t12], "verified": v12, "source_note": n12})
        rows.append({"state_name": state, "year": 2020, "id_stringency_tier": t20,
                     "tier_label": TIER_LABELS[t20], "verified": v20, "source_note": n20})
    return pd.DataFrame(rows)


def main():
    df = build_table()
    df.to_csv("voter_id_stringency.csv", index=False)

    verified_count = df["verified"].sum()
    total = len(df)
    print(f"Saved {total} rows to voter_id_stringency.csv")
    print(f"{verified_count}/{total} rows are sourced/verified; "
          f"{total - verified_count} are defaults -- check the source_note column.")
    print(df[df["verified"] == False]["state_name"].nunique(),  # noqa: E712
          "states have at least one unverified year -- prioritize checking these.")


if __name__ == "__main__":
    main()