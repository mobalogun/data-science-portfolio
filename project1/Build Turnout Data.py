"""
Turnout data for the 2012 and 2020 presidential elections, using
"turnout as a percentage of ballots cast for the highest office" --
i.e., votes for president / voting-eligible population (VEP).

SOURCE: Ballotpedia, "Voter turnout in United States elections,"
https://ballotpedia.org/Voter_turnout_in_United_States_elections
which compiles and cites the United States Elections Project's
"2012 November General Election Turnout Rates" and "2020 November
General Election Turnout Rates" (Dr. Michael McDonald). The US
Elections Project's own turnout data has since moved to the UF
Election Lab (https://election.lab.ufl.edu/).

This script writes both the raw values (for transparency/citation)
and the cleaned, merge-ready CSV in one step.
"""

import pandas as pd

STATE_FIPS = {
    "Alabama": "01", "Alaska": "02", "Arizona": "04", "Arkansas": "05",
    "California": "06", "Colorado": "08", "Connecticut": "09", "Delaware": "10",
    "District of Columbia": "11", "Florida": "12", "Georgia": "13", "Hawaii": "15",
    "Idaho": "16", "Illinois": "17", "Indiana": "18", "Iowa": "19", "Kansas": "20",
    "Kentucky": "21", "Louisiana": "22", "Maine": "23", "Maryland": "24",
    "Massachusetts": "25", "Michigan": "26", "Minnesota": "27", "Mississippi": "28",
    "Missouri": "29", "Montana": "30", "Nebraska": "31", "Nevada": "32",
    "New Hampshire": "33", "New Jersey": "34", "New Mexico": "35", "New York": "36",
    "North Carolina": "37", "North Dakota": "38", "Ohio": "39", "Oklahoma": "40",
    "Oregon": "41", "Pennsylvania": "42", "Rhode Island": "44", "South Carolina": "45",
    "South Dakota": "46", "Tennessee": "47", "Texas": "48", "Utah": "49",
    "Vermont": "50", "Virginia": "51", "Washington": "53", "West Virginia": "54",
    "Wisconsin": "55", "Wyoming": "56",
}

# turnout_rate = votes for highest office (president) / voting-eligible population, in percent
TURNOUT_2012 = {
    "Alabama": 58.60, "Alaska": 58.70, "Arizona": 52.60, "Arkansas": 50.70,
    "California": 55.10, "Colorado": 69.90, "Connecticut": 61.30, "Delaware": 62.30,
    "District of Columbia": 61.50, "Florida": 62.80, "Georgia": 59.00, "Hawaii": 44.20,
    "Idaho": 59.80, "Illinois": 58.90, "Indiana": 55.20, "Iowa": 70.30, "Kansas": 56.90,
    "Kentucky": 55.70, "Louisiana": 60.20, "Maine": 68.20, "Maryland": 66.60,
    "Massachusetts": 65.90, "Michigan": 64.70, "Minnesota": 76.00, "Mississippi": 59.30,
    "Missouri": 62.20, "Montana": 62.50, "Nebraska": 60.30, "Nevada": 56.40,
    "New Hampshire": 70.20, "New Jersey": 61.50, "New Mexico": 54.60, "New York": 53.10,
    "North Carolina": 64.80, "North Dakota": 59.80, "Ohio": 64.50, "Oklahoma": 49.20,
    "Oregon": 63.10, "Pennsylvania": 59.50, "Rhode Island": 58.00, "South Carolina": 56.30,
    "South Dakota": 59.30, "Tennessee": 51.90, "Texas": 49.60, "Utah": 55.50,
    "Vermont": 60.70, "Virginia": 66.10, "Washington": 64.80, "West Virginia": 46.30,
    "Wisconsin": 72.90, "Wyoming": 58.60,
}

TURNOUT_2020 = {
    "Alabama": 66.21, "Alaska": 68.41, "Arizona": 65.27, "Arkansas": 55.86,
    "California": 67.41, "Colorado": 75.51, "Connecticut": 70.07, "Delaware": 70.00,
    "District of Columbia": 63.69, "Florida": 71.17, "Georgia": 67.72, "Hawaii": 57.00,
    "Idaho": 67.15, "Illinois": 66.84, "Indiana": 60.66, "Iowa": 72.85, "Kansas": 65.79,
    "Kentucky": 64.51, "Louisiana": 63.67, "Maine": 75.51, "Maryland": 70.41,
    "Massachusetts": 71.58, "Michigan": 73.37, "Minnesota": 79.57, "Mississippi": 59.67,
    "Missouri": 65.74, "Montana": 72.33, "Nebraska": 69.13, "Nevada": 65.25,
    "New Hampshire": 74.58, "New Jersey": 73.87, "New Mexico": 60.97, "New York": 63.03,
    "North Carolina": 71.20, "North Dakota": 64.02, "Ohio": 66.85, "Oklahoma": 54.84,
    "Oregon": 74.28, "Pennsylvania": 70.69, "Rhode Island": 64.75, "South Carolina": 64.01,
    "South Dakota": 65.21, "Tennessee": 59.59, "Texas": 60.24, "Utah": 67.91,
    "Vermont": 73.50, "Virginia": 71.99, "Washington": 75.17, "West Virginia": 57.00,
    "Wisconsin": 75.50, "Wyoming": 64.16,
}


def main():
    rows = []
    for state, fips in STATE_FIPS.items():
        rows.append({
            "state_name": state, "state": fips, "year": 2012,
            "turnout_rate": TURNOUT_2012[state],
        })
        rows.append({
            "state_name": state, "state": fips, "year": 2020,
            "turnout_rate": TURNOUT_2020[state],
        })

    df = pd.DataFrame(rows)
    df.to_csv("turnout_clean.csv", index=False)
    print(f"Saved {len(df)} rows to turnout_clean.csv")
    print(df.head())


if __name__ == "__main__":
    main()