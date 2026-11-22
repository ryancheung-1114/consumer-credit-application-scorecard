"""Locations shared by the scoring and research entry points."""
import os
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
DATA_SOURCE = Path(os.environ.get("LENDING_CLUB_DATA", PROJECT_DIR / "data" / "latest_merged_union.csv"))
DATA_DICTIONARY = Path(os.environ.get("LENDING_CLUB_DICTIONARY", PROJECT_DIR / "data" / "LCDataDictionary.xlsx"))
