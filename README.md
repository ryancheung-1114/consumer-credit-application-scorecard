# Consumer Credit Application Scorecard

A reproducible study of a consumer credit application scorecard using **Lending Club Data**. The study covers exploratory analysis, sample design, variable review, WoE binning, logistic regression, temporal validation and alternative feature-selection methods.

The primary model uses annual income, debt-to-income ratio, revolving utilisation, loan purpose and enquiries in the preceding six months. A common score is mapped to separate 36- and 60-month probabilities using calibrated intercepts. The target is a **recorded contract outcome** with Fully Paid coded Good and Charged Off or Default coded Bad.

## Main findings

| January–March 2015 model | Log loss | AUC |
|---|---:|---:|
| Five-variable WoE | 0.466607 | 0.6449 |
| Five-field engineered WoE | 0.466453 | 0.6452 |
| Selected business WoE | 0.466838 | 0.6440 |
| WoE with listed-amount ratio | 0.468265 | 0.6421 |
| Engineered main effects | 0.463457 | 0.6549 |
| Pattern based full ridge | 0.463339 | 0.6556 |
| Pattern based RF selection | 0.468003 | 0.6409 |

All seven versions use 2014 term-intercept calibration and the same 84,175 labelled loans. The broader pattern-based model reduced log loss by 0.70% and required 42 encoded columns. Compact engineering within the original five fields reduced loss by 0.033%. Selecting five WoE components from a wider pool added a sixth raw field and supplied no consistent gain. The listed-amount candidate requires evidence of the amount captured before scoring. The original five-variable WoE scorecard remains the primary model.

The primary scorecard predicted a mean Bad rate of 17.54% against 18.98% observed. Calibration errors were larger in some lower-risk 60-month groups. The cutoff simulation describes retained shares among originated loans.

## Report and notebooks

The 34-page English paper includes the compact WoE experiments in Section 6.4 and the seven-model comparison in Table 31. The presentation notebooks run from the packaged aggregate evidence. Rebuilding the research requires the original local inputs described below.

- [Integrated research paper in Word](reports/Consumer_Credit_Application_Scorecard_Research_Paper_20261122.docx)
- [Study overview and EDA evidence](notebooks/01_study_overview.ipynb)
- [Score an application and reconcile its points](notebooks/02_score_applications.ipynb)
- [Feature engineering and RF selection results](notebooks/03_model_comparisons.ipynb)
- [Engineering within the original five fields](notebooks/04_compact_engineered_woe.ipynb)
- [Business feature engineering and five-component selection](notebooks/05_business_feature_selection.ipynb)
- [All seven models under the same later-period comparison](results/all_models_2015Q1.csv)
- [Full-precision scorecard specification](models/scorecard_spec.json)
- [Readable point table](models/scorecard_points.csv)
- [Full comparison by period, term and outcome scenario](results/model_comparison.csv)

## Quick start

Use Python 3.12 or 3.13 and install the tested dependencies.

~~~bash
python -m pip install -r requirements.txt
python src/score.py --input data/synthetic_applications.csv --output results/scored_applications.csv
python scripts/verify_project.py
~~~

The synthetic example returns 554.54 points, with a recorded-Bad probability of 17.94% at 36 months and 33.32% at 60 months. Both records have the same five predictor values.

| Input column | Meaning |
|---|---|
| annual_inc | Reported annual income in source monetary units |
| dti | Debt-to-income ratio in percentage points |
| revol_util | Revolving utilisation in percentage points, optionally with a percent suffix |
| purpose | Source purpose category such as debt_consolidation |
| inq_last_6mths | Enquiries in the preceding six months |
| term_months | Application-confirmed term, 36 or 60 |

The output includes bins, point contributions, total score, Bad probability and review flags. Parameters are loaded from the model specification.

## Study design

| Origination period | Loans with outcomes | Use |
|---|---:|---|
| 2010–2012 | 86,624 | Estimate transformations, WoE and logistic coefficients |
| 2013 | 134,814 | Compare models and define risk groups |
| 2014 | 235,619 | Test original probabilities and fit updated term intercepts |
| January–March 2015 | 84,175 | Evaluate fixed versions on the later cohort |

The 2015 Q1 population also has 102 unresolved loans, all at 60 months. Sensitivity results assign these cases to each outcome extreme. The EDA covers 2,925,492 loans from June 2007 to September 2020. Its compact risk reference uses the 227,967 standard-policy loans originated through December 2013.

## Reproduce the research

The stage runner invokes the original scripts adapted to relative project locations. Supply the exact Lending Club Data extract and the supplied data dictionary described in [data setup](data/README.md).

~~~bash
python scripts/run_research.py --source /path/to/LendingClubData.csv --dictionary /path/to/LCDataDictionary.xlsx --stages all
~~~

Individual stages can be rerun after their dependencies have been generated. The compact engineering stages are compact-woe and business-woe. Their complete Python implementations and aggregate evidence are in the corresponding research folders.

~~~bash
python scripts/run_research.py --source /path/to/LendingClubData.csv --dictionary /path/to/LCDataDictionary.xlsx --stages sample prepare binning1 binning2 logistic term slope oot recalibrate final
~~~

Generated loan-level files stay in the local research folders and are ignored by Git. Aggregate study tables, the model specification and executed presentation notebooks are included. The input fingerprint is recorded in data/source_identity.json. The runner checks it before preparing the research sample.

## Project structure

~~~text
data/          Input description, source identity and synthetic applications
models/        Frozen WoE rules, coefficients, calibration and points
notebooks/     Five executed overview, scoring and comparison notebooks
reports/       Integrated English research paper
results/       Compact published metrics and comparison tables
src/           Standalone application scorer
scripts/       Research runner and delivery verification
research/      Stage scripts and supporting aggregate evidence
~~~

## Interpretation and limits

The analysis concerns historical accepted and originated loans. The recorded-contract target has different follow-up lengths across terms and cohorts. A common historical observation endpoint and original input capture timestamps remain to be established for a fixed-window deployment study. The member identifier is unavailable for repeat-borrower grouping.

Later model experiments used cohorts whose earlier WoE results were already known. Their comparisons document this research process. Paired intervals condition on fixed predictions and use a loan-level independence approximation. Performance on a current full applicant population and the financial effect of an operating cutoff require separate evidence.

## Package verification

The standalone scoring command and three presentation notebooks were executed in the packaged layout. The core logistic, term-intercept, slope, 2014 validation, recalibration and final-scoring stages were rerun from the frozen local development samples with the original Lending Club Data extract supplied to the later-sample loader. Their published scoring results were reconciled with the established study. The complete upstream source preparation remains available through the stage runner.

The Word manuscript was rendered in Microsoft Word and checked across its 33 pages, including 26 figures and 36 tables. The full audit scope is recorded in results/reproducibility.json.

## Method references

- Anderson, R. (2007). *The Credit Scoring Toolkit*. Oxford University Press.
- Baesens, B., Rösch, D., & Scheule, H. (2016). *Credit Risk Analytics*. Wiley.
- [scikit-learn logistic regression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html)
- [Permutation importance](https://scikit-learn.org/stable/modules/permutation_importance.html)
- [2026 supervisory model-risk guidance](https://www.federalreserve.gov/supervisionreg/srletters/sr2602a1.pdf)
