"""Score application rows from the frozen five-variable WoE specification."""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import expit

PROJECT_DIR = Path(__file__).resolve().parents[1]
TERMS = (36, 60)
def probability(pooled, term, calibration):
    offsets = {int(term): row["offset"] for term, row in calibration.items()}
    slopes = {int(term): row["slope"] for term, row in calibration.items()}
    return expit(term.map(offsets) + term.map(slopes) * pooled)

def apply_bins(values, field, rule):
    raw = values.astype("string").str.strip().replace("", pd.NA)
    if rule["type"] == "category":
        labels = raw.str.lower().map(rule["mapping"]).fillna("[UNSEEN]").astype("string")
    else:
        numeric_text = raw if field == "inq_last_6mths" else raw.str.replace(r"%$", "", regex=True).str.strip()
        numbers = pd.to_numeric(numeric_text, errors="coerce").astype(float)
        special = {"0", "[MISSING]", "[INVALID]"}
        labels = pd.cut(numbers, [-np.inf, *rule["cuts"], np.inf],
                        labels=[name for name in rule["woe"] if name not in special],
                        right=False).astype("string")
        if rule.get("separate_zero", False):
            labels.loc[numbers.eq(0)] = "0"
        invalid = raw.notna() & (~np.isfinite(numbers) | numbers.lt(0))
        if field == "annual_inc":
            invalid |= numbers.eq(0)
        if rule.get("whole_number", False):
            invalid |= numbers.mod(1).abs().gt(1e-9)
        labels.loc[invalid] = "[INVALID]"
    labels.loc[raw.isna()] = "[MISSING]"
    return labels

def score_applications(applications, model):
    """Apply the points table and the primary probability mapping to raw columns."""
    terms = pd.to_numeric(applications.term_months.astype("string").str.strip()
                          .str.replace(r"\s+months?$", "", regex=True), errors="coerce")
    if not terms.isin(TERMS).all():
        raise ValueError("term_months must contain 36 or 60.")
    scores = pd.DataFrame({"term_months": terms.astype(int)}, index=applications.index)
    point_columns, review_columns = [], []
    for field, coefficient in model["coefficients"].items():
        rule = model["binning_rules"][field]
        labels = apply_bins(applications[field], field, rule)
        scores[field + "_bin"] = labels
        point_columns.append(field + "_points")
        review_columns.append(field + "_review")
        scores[point_columns[-1]] = -model["scale"]["factor"] * coefficient * labels.map(rule["woe"])
        scores[review_columns[-1]] = ~labels.isin(rule["trained_bins"])
        assert np.isfinite(scores[point_columns[-1]]).all()
    scores["score"] = model["scale"]["base_points"] + scores[point_columns].sum(axis=1)
    recovered = (model["scale"]["origin"] - scores.score) / model["scale"]["factor"]
    scores["probability_bad"] = probability(recovered, terms, model["calibration"][model["primary_model"]])
    scores["review_required"] = scores[review_columns].any(axis=1)
    return scores

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model", type=Path, default=PROJECT_DIR / "models/scorecard_spec.json")
    args = parser.parse_args()
    if args.input.resolve() == args.output.resolve():
        parser.error("Choose an output path different from the input CSV.")
    model = json.loads(args.model.read_text(encoding="utf-8"))
    applications = pd.read_csv(args.input, dtype="string", keep_default_na=False)
    scored = score_applications(applications, model)
    result = applications.join(scored.drop(columns="term_months"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)
    print(f"Scored {len(result):,} applications.")

