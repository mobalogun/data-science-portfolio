# Projects
This section documents my data science projects, research questions, and data stories I create throughout the semester.

---

## Project 1: Voter ID Laws and Voter Turnout

### 1. Problem Definition

**Research question:** Is there a relationship between the stringency of a state's voter ID law and its voter turnout rate in U.S. presidential elections?

**Context:** Voter ID laws have been one of the most contested issues in American election administration over the past two decades. Proponents argue that ID requirements protect election integrity and public confidence in the vote, while critics argue that they create an additional barrier that disproportionately affects certain voters — particularly those who are lower-income, elderly, or lack easy access to the documentation required. Since the Supreme Court's 2008 decision in *Crawford v. Marion County Election Board* upheld Indiana's photo ID law, more states have adopted or tightened ID requirements, making this a live and evolving area of election law. This project looks at two presidential election years — 2012 and 2020 — chosen because they bracket a period of significant change in voter ID law (several major state laws were enacted, blocked by courts, or took effect for the first time during this window), and because national turnout rose sharply between them.

**Why it matters:** This question sits at the intersection of my two majors. For political science, it's a live policy debate with real consequences for representation. For data science, it's a case study in how a social/legal variable that resists easy quantification (a state's "stringency") can still be operationalized and analyzed alongside more standard demographic data — while being honest about the limits of that operationalization.

### 2. Data Description

**Unit of analysis:** One row = one state (plus D.C.) in one presidential election year (2012 or 2020). 102 rows total.

**Key variables:**

| Variable | Conceptualization | Operationalization | Source |
|---|---|---|---|
| Voter ID stringency | How strict a state's ID requirement is | 3-tier ordinal scale: 0 = no ID required, 1 = ID requested but a voter without one can still cast a ballot that counts (affidavit/non-strict), 2 = strict requirement (provisional ballot + follow-up action required) | Hand-coded from Ballotpedia and NCSL reporting, cross-checked against known court rulings |
| Voter turnout rate | Share of eligible population that voted | Votes for president ÷ voting-eligible population (VEP), as a percentage | United States Elections Project (Dr. Michael McDonald), accessed via Ballotpedia's compiled tables |
| Median household income | State-level economic context | ACS5 estimate, variable B19013_001E | U.S. Census Bureau, American Community Survey 5-Year Estimates |
| % bachelor's degree or higher | State-level education context | ACS5 Data Profile estimate (variable code varies by vintage: DP02_0067PE for the 2008–2012 estimates, DP02_0068PE for the 2016–2020 estimates) | U.S. Census Bureau, American Community Survey 5-Year Estimates |

**ACS vintage note:** ACS 5-Year Estimates are named for the *end* year of a rolling 5-year window. The "2012" ACS5 file covers 2008–2012, and the "2020" ACS5 file covers 2016–2020 — each aligns with the corresponding presidential election year.

**Data sources and access:**
- U.S. Census Bureau ACS5 API: `https://api.census.gov/data/{year}/acs/acs5` and `.../acs5/profile`
- United States Elections Project turnout tables, accessed via Ballotpedia's "Voter turnout in United States elections" compilation: `https://ballotpedia.org/Voter_turnout_in_United_States_elections`
- Voter ID stringency: hand-coded from Ballotpedia's 2012 general election coverage and NCSL's voter ID law tracking, with several entries defaulted to current classifications pending further verification (see Limitations)

**Size and assumptions:** 102 rows (50 states + D.C. × 2 years). No U.S. territories included. D.C. is included as its own unit despite not being a state, consistent with how the turnout and ACS sources both report it.

### 3. Data Cleaning and Preparation

Three raw sources were pulled and cleaned independently before merging:

- **ACS pull (`census_pull.py`):** Queried the Census API separately for each year's income (`B19013_001E`) and education data. Because the Data Profile's variable numbering for "% bachelor's or higher" shifted between the 2012 and 2020 ACS5 vintages (`DP02_0067PE` vs. `DP02_0068PE`), the script dynamically looks up the correct variable code each year by matching on its label text rather than relying on a single hardcoded code — this was caught during testing when a hardcoded code silently returned raw population counts instead of percentages for 2012.
- **Turnout data (`build_turnout_data.py`):** Built directly from the U.S. Elections Project's presidential turnout-rate tables (accessed via Ballotpedia), using the "turnout as a percentage of ballots cast for the highest office" figure so that every state has a complete, non-missing value for both years.
- **Voter ID stringency (`voter_id_stringency.py`):** Hand-coded on the 3-tier scale described above. States with a specific, sourced classification (e.g., the 2012 Ballotpedia election-day summary, or court records showing a law was blocked) are flagged `verified = True`; the rest default to a current-day classification and are flagged `verified = False` pending further check, with a `source_note` explaining the reasoning or the specific concern for that state-year.

**Merging:** The three cleaned files were joined in two steps (`merge_data.py`): ACS and turnout data were joined on FIPS state code + year, then voter ID stringency was joined on state name + year (since the hand-coded table doesn't carry a FIPS code). All 102 rows matched successfully on the second join — no rows were dropped, and there is no missing data in the final merged dataset.

**Key cleaning decisions:**
- FIPS codes from the Census API were zero-padded to 2 digits before joining, since some come back without leading zeros.
- Turnout percentages were kept on a 0–100 scale throughout rather than as fractions, to match how the ACS percentage variable is already returned by the Census API.

### 4. Visualizations and Insights

**Chart 1: Voter Turnout by ID Law Stringency, 2012 vs. 2020 (scatter)**

`[FILL IN: embed chart1_turnout_vs_stringency_scatter.png here]`

Each point is one state in one election year. Turnout is generally higher and more spread out among no-ID states, while strict-ID states cluster somewhat lower.

**Chart 2: Average Turnout by Stringency Tier, 2012 vs. 2020 (bar)**

`[FILL IN: embed chart2_avg_turnout_by_tier_bar.png here]`

Average turnout drops in a consistent step pattern as stringency increases, in both years:

| Stringency Tier | 2012 Avg. Turnout | 2020 Avg. Turnout |
|---|---|---|
| No ID required | 61.0% | 69.9% |
| ID requested/non-strict | 60.3% | 66.6% |
| Strict ID required | 56.7% | 65.6% |

The gap between "no ID" and "strict ID" states is nearly identical across the two years — about 4.4 percentage points in 2012 and 4.3 points in 2020 — even though national turnout rose substantially between the two elections. This stability suggests the pattern isn't just an artifact of one unusually high- or low-turnout year.

### 5. Storytelling and Narrative

The headline finding is a consistent, modest negative association between voter ID stringency and turnout: states with no ID requirement out-turned states with non-strict requirements, which in turn out-turned states with strict requirements — and this ordering held in both 2012 and 2020 individually, not just on average across both years combined.

`[FILL IN once check_controls.py is run:]` After controlling for median household income and the share of the population with a bachelor's degree or higher, the stringency effect [FILL IN: shrank substantially / held up / flipped sign — describe what the regression output showed]. [FILL IN: coefficient value] This [FILL IN: strengthens / weakens / complicates] the case that ID stringency itself, rather than the demographic and economic profile of the states that adopt strict laws, is driving the turnout gap.

**What this data can't tell us:** A negative association between stringency and turnout is consistent with several different explanations — the ID law directly deterring or blocking some voters, or states that adopt strict ID laws differing in other ways (political culture, competitiveness of elections, campaign mobilization effort) that independently affect turnout. With only two years and state-level (not individual-level) data, this project can describe a pattern but cannot establish that voter ID laws *cause* lower turnout.

### 6. Limitations, Ethics, and Reflection

- **Sample size:** With 102 state-year observations, this dataset is not large enough to support strong causal claims, especially once split across three tiers and two years — some cells represent a small number of states.
- **Voter ID stringency coding is largely unverified:** Roughly three-quarters of the state-year stringency codings are defaults based on current-day classification rather than a law verified as being in effect for that specific historical election, because voter ID law is heavily litigated and frequently changed (several states had laws passed, blocked by courts, or delayed between 2012 and 2020). The ~20 fully sourced entries (including an important correction for North Carolina, whose 2018 photo ID law was blocked by courts through the entire 2020 general election) show that naively using current-day classifications for historical years can be actively wrong, not just imprecise. This is the single biggest limitation of the analysis and would be the first thing to fix with more time.
- **What's missing:** This project only looks at the *existence* of a law on paper, not how strictly it was enforced in practice, how well it was communicated to voters, or whether cure processes for provisional ballots were accessible. It also doesn't capture county-level variation within states, individual-level voter experience, or a rural/urban control (the ACS does not have a single clean state-level urban percentage variable, which is a documented gap).
- **Potential biases:** The "stringency" coding itself involves judgment calls about how to categorize laws with unusual provisions (e.g., religious-objection exceptions, or laws that were only partially enjoined). A different coder might draw the tier boundaries slightly differently.
- **Ethical note on the underlying topic:** Voter ID policy affects who can easily participate in democracy, and the same underlying data can be — and has been — used to argue for opposite policy conclusions. I've tried to present the association here descriptively rather than as proof of a particular political narrative in either direction.
- **What I'd explore next:** Extending to all five election years from 2012–2020 rather than just the two endpoints, fully verifying every stringency coding against primary legal sources rather than a mix of verified and default entries, and adding a rural/urban proxy variable.

### 7. Code and Transparency

- **Repository/notebook:** `[FILL IN: link to your GitHub repo/notebook once pushed]`
- **Data sources cited:**
  - U.S. Census Bureau. *American Community Survey 5-Year Estimates*, 2008–2012 and 2016–2020. https://www.census.gov/data/developers/data-sets/acs-5year.html
  - McDonald, M. (n.d.). *United States Elections Project: Voter Turnout Data*. Accessed via Ballotpedia, "Voter turnout in United States elections." https://ballotpedia.org/Voter_turnout_in_United_States_elections
  - Ballotpedia and National Conference of State Legislatures. *Voter Identification Requirements*. https://ballotpedia.org and https://www.ncsl.org
- **AI usage disclosure:** Claude (Anthropic) was used throughout this project to help write and debug the Python data-pull and cleaning scripts (Census API pull, turnout data compilation, merge script, and control-variable regression check), to research and cross-check historical voter ID law status for specific states and years, and to help structure this write-up. All research design choices, data interpretation, and final written analysis are my own.

### Academic References (APA)

`[FILL IN: 3 peer-reviewed sources — see suggestions below]`

1.
2.
3.
