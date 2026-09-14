"""
Generates the two visualizations for the projects.md writeup:
  1. Scatter: turnout rate vs. voter ID stringency tier (colored by year)
  2. Bar chart: average turnout by stringency tier, 2012 vs 2020

Run after merge_data.py has produced analysis_dataset.csv.
Outputs two PNG files you can embed directly in projects.md.
"""

import pandas as pd
import matplotlib.pyplot as plt

def main():
    df = pd.read_csv("analysis_dataset.csv")

    # ---------- Chart 1: scatter, turnout vs. stringency tier ----------
    fig, ax = plt.subplots(figsize=(8, 6))

    colors = {2012: "#4C72B0", 2020: "#DD8452"}
    for year, group in df.groupby("year"):
        # jitter the x position slightly so points at the same tier don't
        # all stack directly on top of each other
        jitter = (group.index % 7 - 3) * 0.03
        ax.scatter(
            group["id_stringency_tier"] + jitter,
            group["turnout_rate"],
            alpha=0.7,
            label=str(year),
            color=colors.get(year, "gray"),
        )

    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels(["No ID\nrequired", "ID requested/\nnon-strict", "Strict ID\nrequired"])
    ax.set_xlabel("Voter ID Stringency Tier")
    ax.set_ylabel("Turnout Rate (% of voting-eligible population)")
    ax.set_title("Voter Turnout by ID Law Stringency, 2012 vs. 2020")
    ax.legend(title="Election Year")
    ax.grid(axis="y", alpha=0.3)

    fig.tight_layout()
    fig.savefig("chart1_turnout_vs_stringency_scatter.png", dpi=150)
    print("Saved chart1_turnout_vs_stringency_scatter.png")

    # ---------- Chart 2: bar chart, avg turnout by tier, 2012 vs 2020 ----------
    avg_turnout = (
        df.groupby(["id_stringency_tier", "year"])["turnout_rate"]
        .mean()
        .unstack("year")
    )

    fig2, ax2 = plt.subplots(figsize=(8, 6))
    avg_turnout.plot(kind="bar", ax=ax2, color=[colors.get(c, "gray") for c in avg_turnout.columns])

    ax2.set_xticklabels(["No ID\nrequired", "ID requested/\nnon-strict", "Strict ID\nrequired"], rotation=0)
    ax2.set_xlabel("Voter ID Stringency Tier")
    ax2.set_ylabel("Average Turnout Rate (%)")
    ax2.set_title("Average Turnout by Stringency Tier: 2012 vs. 2020")
    ax2.legend(title="Election Year")
    ax2.grid(axis="y", alpha=0.3)

    # annotate bars with the actual values
    for container in ax2.containers:
        ax2.bar_label(container, fmt="%.1f", padding=2)

    fig2.tight_layout()
    fig2.savefig("chart2_avg_turnout_by_tier_bar.png", dpi=150)
    print("Saved chart2_avg_turnout_by_tier_bar.png")

    # Print the underlying numbers too, useful for your narrative section
    print("\nAverage turnout by tier and year:")
    print(avg_turnout)

if __name__ == "__main__":
    main()