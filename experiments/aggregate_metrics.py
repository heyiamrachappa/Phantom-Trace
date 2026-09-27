import json, os, glob
from pathlib import Path
from collections import defaultdict
import numpy as np

ROOT = Path('.').resolve()
METRICS_DIR = ROOT / 'results/metrics/v3'
all_files = glob.glob(str(METRICS_DIR / '*_metrics.json'))

agg = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list))))
for fpath in all_files:
    with open(fpath, 'r') as f:
        r = json.load(f)
    st = r["strategy"]
    sc = r["schema"]
    mo = r["model"]
    mets = r["test_metrics"]
    for k, v in mets.items():
        if isinstance(v, (int, float)) and v is not None:
            agg[st][sc][mo][k].append(v)
            
summary_table = {}
for st in agg:
    summary_table[st] = {}
    for sc in agg[st]:
        summary_table[st][sc] = {}
        for mo in agg[st][sc]:
            summary_table[st][sc][mo] = {}
            for k, vals in agg[st][sc][mo].items():
                summary_table[st][sc][mo][k] = {
                    "mean": round(float(np.mean(vals)), 4),
                    "std": round(float(np.std(vals, ddof=1)), 4) if len(vals) > 1 else 0.0,
                    "n_seeds": len(vals),
                    "values": [round(float(x), 4) for x in vals]
                }

with open(METRICS_DIR / "aggregate_summary.json", "w") as f:
    json.dump(summary_table, f, indent=2)
print("Aggregated metrics to aggregate_summary.json")
