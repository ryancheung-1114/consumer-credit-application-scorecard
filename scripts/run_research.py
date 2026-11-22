"""Run the research stages on the recorded Lending Club Data extract."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
STAGES = {
    "eda": ("consumer_credit_application_scorecard_eda_20261108", "recompute_eda.py"),
    "eda-check": ("consumer_credit_application_scorecard_eda_20261108", "verify_numbers.py"),
    "annual": ("consumer_credit_application_scorecard_eda_annual_20261108", "analyse_annual.py"),
    "labels": ("label_definition_sample_eligibility_20261108", "analyse_labels.py"),
    "sample": ("development_sample_20261108", "prepare_development_sample.py"),
    "prepare": ("variable_rules_20261112", "standardise_variables.py"),
    "binning1": ("binning_batch_1_20261114", "binning_analysis.py"),
    "binning2": ("binning_batch_2_20261115", "binning_batch_2.py"),
    "logistic": ("woe_logistic_comparison_20261118", "compare_woe_models.py"),
    "ablation": ("feature_ablation_20261121", "test_feature_ablation.py"),
    "term": ("term_calibration_20261121", "calibrate_by_term.py"),
    "slope": ("term_slope_20261121", "calibrate_60_month_slope.py"),
    "oot": ("oot_validation_20261121", "validate_scorecard_oot.py"),
    "recalibrate": ("recalibration_holdout_20261121", "recalibrate_and_lock_holdout.py"),
    "final": ("scorecard_final_20261121", "scorecard.py"),
    "elastic": ("elastic_net_20261122", "elastic_net.py"),
    "engineering": ("feature_engineering_selection_20261122", "feature_engineering_selection.py"),
    "engineered-oot": ("engineered_scorecard_oot_20261122", "validate_engineered_oot.py"),
    "rf": ("random_forest_feature_selection_20261122", "pattern_rf_selection.py"),
    "compact-woe": ("five_field_engineered_woe_20261122", "engineer_five_woe.py"),
    "business-woe": ("business_feature_woe_selection_20261122", "business_woe_selection.py"),
    "correlation": ("eda_correlation_review_20261121", "correlation_review.py"),
}

def digest(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--dictionary", type=Path, required=True)
    parser.add_argument("--stages", nargs="+", default=["all"])
    args = parser.parse_args()
    stages = list(STAGES) if args.stages == ["all"] else args.stages
    unknown = set(stages) - set(STAGES)
    if unknown:
        parser.error(f"Unknown stages: {', '.join(sorted(unknown))}")
    source, dictionary = args.source.resolve(), args.dictionary.resolve()
    expected = json.loads((ROOT / "data/source_identity.json").read_text(encoding="utf-8"))
    if source.stat().st_size != expected["source_bytes"] or digest(source) != expected["source_sha256"]:
        raise ValueError("The CSV differs from the recorded Lending Club Data input.")
    if not dictionary.is_file():
        raise FileNotFoundError(dictionary)
    reference = dict(expected, source=str(source), source_mtime_ns=source.stat().st_mtime_ns)
    path = ROOT / "research/development_sample_20261108/inputs/source_reference.json"
    path.write_text(json.dumps(reference, indent=2),encoding="utf-8")
    environment = os.environ.copy()
    environment.update(LENDING_CLUB_DATA=str(source), LENDING_CLUB_DICTIONARY=str(dictionary),
                       OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1",
                       PYTHONIOENCODING="utf-8", MPLBACKEND="Agg")
    for name in stages:
        folder, filename = STAGES[name]
        script = ROOT / "research" / folder / filename
        print(f"Running {name}", flush=True)
        subprocess.run([sys.executable, str(script)], cwd=script.parent, env=environment, check=True)
