"""Check the frozen point equation, published examples and delivery files."""
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import expit

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("scorecard", ROOT / "src/score.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
model = json.loads((ROOT / "models/scorecard_spec.json").read_text(encoding="utf-8"))
applications = pd.read_csv(ROOT / "data/synthetic_applications.csv", dtype="string", keep_default_na=False)
scored = module.score_applications(applications,model)
expected = pd.read_csv(ROOT / "research/scorecard_final_20261121/results/scoring_example.csv")
np.testing.assert_allclose(scored["score"], expected["score"], atol=1e-10, rtol=0)
np.testing.assert_allclose(scored.probability_bad,expected.probability_bad,atol=1e-12,rtol=0)
weights = model["coefficients"]
log_odds = np.full(len(scored),model["model_intercept"])
for field,beta in weights.items():
    log_odds += beta * scored[field+"_bin"].map(model["binning_rules"][field]["woe"]).to_numpy()
term = applications.term_months.astype(int)
adjust = model["calibration"][model["primary_model"]]
offset = term.map({int(t):row["offset"] for t,row in adjust.items()})
np.testing.assert_allclose(expit(log_odds+offset),scored.probability_bad,atol=1e-12,rtol=0)
assert not scored.review_required.any()
comparison = pd.read_csv(ROOT / "results/model_comparison.csv")
q1=comparison.loc[comparison.cohort.eq("2015 Q1") & comparison.calibration.eq("2014 offsets")
                  & comparison.scenario.eq("Recorded outcomes") & comparison["sample"].eq("All loans")]
assert len(q1)==4 and q1.loans.eq(84175).all() and q1.bad.eq(15978).all()
assert len(list((ROOT / "reports").glob("*.docx")))==1
print("Verified scoring examples, direct logistic probabilities, and the published comparison population.")



all_models = pd.read_csv(ROOT / "results/all_models_2015Q1.csv")
assert len(all_models) == 7
assert all_models.loans.eq(84175).all() and all_models.bad.eq(15978).all()
assert all_models.calibration.eq("2014 offsets").all()
assert np.isfinite(all_models[["log_loss", "auc", "brier"]].to_numpy()).all()
print("Verified all seven later-period model rows and their common outcome population.")
