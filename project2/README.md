# Project 2: Predicting Supreme Court Case Outcomes

Binary classification of U.S. Supreme Court case outcomes (petitioner win vs. loss) using pre-decision case characteristics from the Supreme Court Database (SCDB), 2000–2025 terms.

Full write-up: [Projects page](https://mobalogun.github.io/data-science-portfolio/projects.html#project-2-predicting-supreme-court-case-outcomes)

## Contents

- `01_data_cleaning_eda.ipynb` — loads the raw SCDB file, scopes it to 2000–2025, cleans the target variable, checks missingness, and explores feature distributions.
- `02_modeling.ipynb` — train/test split, baseline, logistic regression, random forest, evaluation metrics, confusion matrices, ROC curves, coefficient and feature-importance interpretation, error analysis.
- `03_extensions.ipynb` — two follow-up experiments: cross-validation-tuned classification threshold, and a time-based train/test split (2000–2019 train, 2020–2025 test).
- `scdb_cleaned_2000_2025.csv` — the cleaned, scoped dataset produced by the first notebook and used as input to the second and third.
- `SCDB_2026_01_caseCentered_Citation.csv` — the raw source data (Supreme Court Database, 2026 Release 01, case-centered, organized by citation). Downloaded from [scdb.la.psu.edu](http://scdb.la.psu.edu).

## Running it

```
pip install pandas numpy matplotlib seaborn scikit-learn jupyter
jupyter notebook
```

Run the notebooks in order: `01` → `02` → `03`.

## Data source

Supreme Court Database (SCDB), 2026 Release 01. http://scdb.la.psu.edu

## AI usage disclosure

Claude (Anthropic) was used to help build and debug these notebooks, research and summarize academic background sources, and help structure the write-up. All scoping decisions, interpretation, and final written analysis are my own.
