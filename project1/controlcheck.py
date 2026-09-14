"""
Checks whether the turnout ~ stringency relationship holds up once you
account for income and education -- i.e., is this just proxying for
richer/more-educated states happening to have looser ID laws?

Uses plain OLS via numpy (no statsmodels dependency needed).
"""

import numpy as np
import pandas as pd

def ols(X, y):
    """Simple OLS with an intercept column added automatically."""
    X = np.column_stack([np.ones(len(X)), X])
    coefs, residuals, rank, sv = np.linalg.lstsq(X, y, rcond=None)
    y_pred = X @ coefs
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r_squared = 1 - ss_res / ss_tot
    return coefs, r_squared

def main():
    df = pd.read_csv("analysis_dataset.csv").dropna(
        subset=["turnout_rate", "id_stringency_tier", "median_hh_income", "pct_bachelors_or_higher"]
    )

    print(f"N = {len(df)} state-year observations\n")

    # --- Correlation matrix ---
    corr = df[["turnout_rate", "id_stringency_tier", "median_hh_income", "pct_bachelors_or_higher"]].corr()
    print("Correlation matrix:")
    print(corr.round(3))
    print()

    # --- Model 1: turnout ~ stringency only ---
    X1 = df[["id_stringency_tier"]].values
    y = df["turnout_rate"].values
    coefs1, r2_1 = ols(X1, y)
    print("Model 1: turnout_rate ~ id_stringency_tier")
    print(f"  Intercept: {coefs1[0]:.2f}")
    print(f"  Stringency coefficient: {coefs1[1]:.2f}  (R² = {r2_1:.3f})")
    print(f"  Interpretation: each step up in stringency tier is associated with "
          f"a {coefs1[1]:.2f} percentage-point change in turnout, before controls.\n")

    # --- Model 2: turnout ~ stringency + income + education ---
    X2 = df[["id_stringency_tier", "median_hh_income", "pct_bachelors_or_higher"]].values
    coefs2, r2_2 = ols(X2, y)
    print("Model 2: turnout_rate ~ id_stringency_tier + median_hh_income + pct_bachelors_or_higher")
    print(f"  Intercept: {coefs2[0]:.2f}")
    print(f"  Stringency coefficient: {coefs2[1]:.4f}")
    print(f"  Income coefficient (per $1): {coefs2[2]:.5f}")
    print(f"  Education coefficient (per pct point): {coefs2[3]:.3f}")
    print(f"  R² = {r2_2:.3f}\n")

    print("--- What to look for ---")
    print(f"Stringency coefficient WITHOUT controls: {coefs1[1]:.2f}")
    print(f"Stringency coefficient WITH controls:    {coefs2[1]:.2f}")
    if abs(coefs2[1]) < abs(coefs1[1]) * 0.5:
        print("-> The stringency effect shrinks a lot once income/education are added.")
        print("   This suggests income/education may explain much of the raw pattern.")
    elif np.sign(coefs2[1]) != np.sign(coefs1[1]):
        print("-> The stringency effect FLIPS SIGN once controls are added.")
        print("   This is an important finding for your limitations/storytelling section.")
    else:
        print("-> The stringency effect holds up reasonably well even with controls,")
        print("   which strengthens (but does not prove) your research narrative.")

if __name__ == "__main__":
    main()