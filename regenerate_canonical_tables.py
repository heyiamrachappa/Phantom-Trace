import json, os, time
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path("/home/yi/My-Projects/Stealth-Network-Reconnaissance")

# 1. Load V3 aggregate summary
with open(ROOT / "results/metrics/v3/aggregate_summary.json") as f:
    agg = json.load(f)

# 2. Load Deduplication audit
with open(ROOT / "results/audits/domain_and_dedup_audit.json") as f:
    dedup = json.load(f)

# 3. Load Interval ablation
with open(ROOT / "results/ablation/interval_ablation_results.json") as f:
    ablation = json.load(f)

# 4. Load Calibration
with open(ROOT / "results/calibration/calibration_results.json") as f:
    calibration = json.load(f)

# 5. Load Third dataset
with open(ROOT / "results/benchmark/third_dataset_ton_iot_results.json") as f:
    ton_iot = json.load(f)

print("Loaded all 5 output result files successfully.")
