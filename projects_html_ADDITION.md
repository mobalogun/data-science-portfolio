---
## Project 2: Predicting Supreme Court Case Outcomes

**Jump to:** [Problem Definition](#1-problem-definition-2) · [Data Description](#2-data-description-2) · [Data Cleaning](#3-data-cleaning-and-preparation-2) · [Visualizations](#4-visualizations-and-insights-2) · [Baseline & Models](#5-baseline-and-model-development) · [Evaluation](#6-model-evaluation-and-selection) · [Interpretation](#7-model-interpretation-and-insights) · [Limitations](#8-limitations-ethics-and-reflection-2) · [Code & Sources](#9-code-and-transparency-2)

### 1. Problem Definition

**Research question:** Can characteristics of a U.S. Supreme Court case that are known *before* the Court rules — the legal issue area, the direction of the lower court's ruling, how the case reached the Court, and similar procedural facts — predict whether the petitioner (the party asking the Court to review the case) wins?

**Target variable:** `partyWinning` — 1 if the petitioner wins, 0 if the petitioner does not win. This is a binary **classification** problem.

**Who might benefit:** litigants and their attorneys deciding whether an appeal is worth pursuing, journalists and court-watchers trying to anticipate rulings, and researchers studying what actually drives Supreme Court outcomes.

**Why it matters:** the Supreme Court's rulings shape law for the entire country, yet its decision-making is often treated as unpredictable or purely ideological. This project sits squarely at the intersection of my two majors: for political science, it's a direct test of how much of the Court's behavior is structural and procedural versus genuinely case-specific; for data science, it's a case study in building a classifier on real-world, imbalanced, mostly categorical data — and in being honest when the result isn't a clean win for the model.

Predicting judicial behavior has real research history behind it. Katz et al. (2017) built a random forest model on pre-decision Supreme Court Database features across nearly two centuries of cases, reaching about 70% accuracy at the case level. Earlier, Ruger et al. (2004) found a simple statistical model using general case characteristics beat a panel of legal experts at predicting a full Supreme Court term (75% vs. 59.1% accuracy) — a notable result given the model used none of the specific legal reasoning the experts relied on. More recently, Davids (2024) compared several ML algorithms on similar features and found the stated reason certiorari was granted, and the category of the petitioner and appellee, were among the most predictive features — a finding my own model independently reproduces (see Section 7). Full citations are in Section 9.

### 2. Data Description

**Source:** the [Supreme Court Database (SCDB)](http://scdb.la.psu.edu), 2026 Release 01, case-centered version. The SCDB is the standard academic dataset for quantitative research on the Court.

**Unit of analysis:** one row = one case (dispute), not one justice vote.

**Size:** the full database has 9,409 cases spanning 1946–2025. I scoped this project to the **2000–2025 terms** (1,954 cases), narrowed to **1,949 cases** after removing 5 with an unclear or missing outcome.

**Why 2000–2025:** the Court's composition and procedures have shifted a lot since 1946, and missingness in several fields is far worse in the older data. Restricting to just the Roberts Court (2005–present) keeps the era more uniform but leaves under 1,600 cases. 2000–2025 is a middle path — it spans two continuous, well-documented eras (the end of the Rehnquist Court and the full Roberts Court) with low missingness, and I kept `chief` as a feature rather than filtering it out, so the model can use the era distinction directly.

**Target variable:** `partyWinning` — 68.5% of cases in this scope were petitioner wins, a real class imbalance that shapes how I evaluate the models later.

**Features used:** `issueArea` (14 categories), `petitioner`/`respondent` type (184/183 categories), `jurisdiction` (7 categories), `caseOrigin`, `caseSource`, `lcDisagreement`, `certReason`, `lcDispositionDirection`, `threeJudgeFdc`, `term`, and `chief`.

**A key limitation of the source itself:** the SCDB only covers cases that received a full, signed opinion — it doesn't include the much larger number of cases the Court declines to hear. My conclusions apply only to cases the Court already chose to decide, not to litigation in general.

### 3. Data Cleaning and Preparation

**Cleaning the target:** I dropped 5 cases with an unclear or missing outcome code (`partyWinning = 2` or missing) — too small and ambiguous a group to safely relabel.

**Missing features:** within this 2000–2025 scope, every candidate feature was missing in under 2% of cases (much cleaner than the ~70–80% missingness seen in state-level fields across the full historical dataset). I filled missing categorical values with an explicit `"missing"` category rather than dropping rows, since for some fields — like `lcDispositionDirection` — the absence of a value is itself informative (e.g., some cases don't have a single ideologically-codable lower court ruling).

**Encoding:** categorical features were one-hot encoded; `term` was kept numeric and standardized.

**Data leakage — what I explicitly excluded:** columns recorded only *after* the Court's decision (`caseDisposition`, `decisionDirection`, `majVotes`, `minVotes`, `splitVote`, `majOpinWriter`, `precedentAlteration`, and related fields) were left out of the feature set entirely. Including any of these would let the model "see" the answer before predicting it.

**Train/test split:** an 80/20 stratified random split, preserving the ~68.5%/31.5% class balance in both sets. I also ran a **time-based split** (train on 2000–2019, test on 2020–2025) as a stress test — see Section 6.

### 4. Visualizations and Insights

**Class balance:** petitioners won 68.5% of cases — a meaningful imbalance that I had to account for throughout modeling and evaluation, not just note in passing.

![Bar chart showing the distribution of case outcomes, petitioner won vs. lost, 2000-2025 terms](https://mobalogun.github.io/data-science-portfolio/chart1_outcome_distribution_bar.png)

**Issue area distribution:** cases are concentrated in a handful of issue areas — criminal procedure, economic activity, civil rights, and judicial power account for the bulk of the dataset, while several others are sparsely represented.

![Horizontal bar chart of number of cases by legal issue area, 2000-2025](https://mobalogun.github.io/data-science-portfolio/chart2_issuearea_cases_bar.png)

Win rates vary meaningfully by issue area and by chief-justice era around the overall 68.5% average, which is exactly the kind of spread a classifier can use — and it directly informed which features I kept.

### 5. Baseline and Model Development

**Baseline:** a classifier that always predicts "petitioner wins." Given the 68.5%/31.5% split, this is a genuinely non-trivial bar — 68.5% accuracy and an F1 of 0.813.

**Model 1 — Logistic Regression:** chosen because the outcome is binary, and logistic regression produces coefficients that convert directly into odds ratios, giving a transparent account of which features push a prediction toward a win or loss.

**Model 2 — Random Forest:** chosen because it can capture interactions between categorical features (e.g., issue area combined with lower court direction) without me specifying them by hand, and it gives a feature-importance ranking as a second way to interpret results. I trained it with `class_weight="balanced"` to counteract the imbalance, since without it the model leans on the ~69% base rate and under-predicts the minority class.

Both models used identical preprocessing and the identical test split, so differences in performance reflect the models, not the data handling.

### 6. Model Evaluation and Selection

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---|---|---|---|---|
| Baseline (majority class) | 0.685 | 0.685 | 1.000 | 0.813 | — |
| Logistic Regression | 0.662 | 0.705 | 0.869 | 0.779 | 0.609 |
| Random Forest (default) | 0.608 | 0.766 | 0.614 | 0.682 | 0.644 |
| **Random Forest (tuned threshold ≈ 0.38)** | **0.690** | 0.690 | 0.993 | **0.814** | **0.644** |

> **Headline finding:** at the default classification threshold, both of my trained models actually scored *below* the majority-class baseline on accuracy and F1 — but their ROC-AUC scores showed they did have real, above-chance discriminative power. Tuning the classification threshold (via cross-validation, never touching the test set) let the random forest finally edge past the baseline.

Accuracy alone is a poor guide here, because a model can score well just by leaning toward the 68.5% majority class without actually distinguishing wins from losses. **ROC-AUC** — how well a model ranks cases by predicted win-probability, independent of any threshold — is the fairer measure of real signal, and it's what separates both trained models from a coin flip.

![ROC curves for logistic regression and random forest on the held-out test set](https://mobalogun.github.io/data-science-portfolio/chart4_roc_curves.png)

**A more realistic stress test — and an honest limitation.** I also retrained the models on a **time-based split**: train on 2000–2019, test on 2020–2025, rather than a random shuffle. This is a harder, more realistic test of predicting *future* cases. It did not go well: the baseline's accuracy actually *rose* to 0.715 (petitioners won more often in 2020–2025), while the random forest's accuracy *fell* to about 0.465.

![Bar chart comparing baseline, logistic regression, and random forest performance when trained on 2000-2019 and tested on 2020-2025](https://mobalogun.github.io/data-science-portfolio/chart6_timebased_split_bar.png)

This is a meaningful, honest result rather than a failure to hide: it shows the model's modest edge over baseline depends on training and test cases coming from a similar time period, and doesn't reliably extend to forecasting genuinely future terms.

**Final model:** the random forest with a cross-validation-tuned threshold, evaluated on the random 80/20 split — the only configuration that beat the baseline on both accuracy and F1 while keeping the strongest ROC-AUC.

### 7. Model Interpretation and Insights

The random forest's most-used features were `certReason`, `lcDisagreement`, `caseSource`, `term`, and `respondent` type.

![Horizontal bar chart of the top 15 most important features in the random forest model](https://mobalogun.github.io/data-science-portfolio/chart5_rf_feature_importance_bar.png)

**`certReason` and party-type category coming out on top closely matches Davids (2024)**, who independently identified the same two feature categories as most influential in a similarly-scoped model of Supreme Court outcomes — a reassuring sign that this isn't an artifact of my specific dataset scope, but reflects a real, previously-documented pattern.

Looking at the cases the random forest got most confidently wrong showed no single obvious pattern — misclassifications spanned multiple issue areas and both chief-justice eras, consistent with the modest (not dominant) predictive power the ROC-AUC scores show.

**What this can, and can't, tell us:** a handful of procedural, pre-decision case facts carry real, non-random signal about who wins, echoing prior research. But the model can't explain *why* a case comes out the way it does, and — per the time-based split result — it shouldn't be trusted to project accurately into future terms.

### 8. Limitations, Ethics, and Reflection

- **Selection bias in the data itself:** the SCDB only includes cases the Court chose to fully hear, not the much larger set of petitions it declines. My conclusions describe that already-selected population, not litigation broadly.
- **Consequences of errors:** if a tool like this were used to inform a real decision (e.g., whether an appeal is worth pursuing), a false positive could encourage a costly appeal unlikely to succeed, while a false negative could discourage a meritorious one. Given the model's modest accuracy, that's a real risk, not a hypothetical one.
- **Not appropriate for real-world decision-making as-is:** the gap between the model's performance on a random split versus a time-based split is the clearest reason why — it describes patterns in cases similar to ones it's already seen, but shouldn't be trusted to forecast a genuinely future case, which is exactly the situation where someone would want a prediction.
- **What I'd explore next:** incorporating the text of party briefs or lower court opinions (a direction Davids (2024) also suggests), engineering features around individual justice ideology scores, and modeling the shift in outcome rates over time explicitly rather than treating `term` as a simple numeric feature.
- **What a user should understand before relying on this model:** it was trained on a specific, non-random sample of cases (2000–2025 only, already selected by the Court), its accuracy is only modestly better than always guessing the majority outcome, and it performs meaningfully worse when asked to predict genuinely future cases.

### 9. Code and Transparency

- **Repository/notebooks:** [Please click here to view the code!](https://github.com/mobalogun/data-science-portfolio/tree/main/project2)
- **Data source:** Supreme Court Database, 2026 Release 01, case-centered, http://scdb.la.psu.edu
- **AI usage disclosure:** Claude was used throughout this project to help build and debug the data cleaning, modeling, and threshold-tuning/time-split extension notebooks, to research and summarize the academic background sources, and to help structure this write-up. All scoping decisions (dataset era, feature selection, which experiments to run), interpretation of results, and final written analysis are my own.

### Academic References (APA)

1. Davids, B. C. (2024). *Forecasting the Supreme Court: A comparative analysis of machine learning algorithms on petitioner vs. appellee outcomes* [Departmental honors thesis, Hood College]. MD-SOAR. http://hdl.handle.net/11603/33254

2. Katz, D. M., Bommarito, M. J., & Blackman, J. (2017). A general approach for predicting the behavior of the Supreme Court of the United States. *PLOS ONE, 12*(4), e0174698. https://doi.org/10.1371/journal.pone.0174698

3. Ruger, T. W., Kim, P. T., Martin, A. D., & Quinn, K. M. (2004). The Supreme Court Forecasting Project: Legal and political science approaches to predicting Supreme Court decisionmaking. *Columbia Law Review, 104*(4), 1150–1210.
