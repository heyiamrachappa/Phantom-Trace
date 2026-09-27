#!/usr/bin/env python3
"""
Phase 3 — Master Full Rerun Script
Executes all 5 models (RF, XGBoost, SVM, Isolation Forest, MLP)
across all 5 random seeds (42, 7, 13, 99, 2024)
for both 11-feature (Primary) and 20-feature (Sensitivity) schemas
across all 5 split conditions:
  - unsw_to_cic (Primary cross-dataset)
  - cic_to_unsw (Reverse cross-dataset)
  - time_wise (Temporal holdout)
  - pcap_wise (Synthetic-to-real transfer)
  - host_wise (Host-disjoint holdout)

Saves:
  - Per-instance predictions: results/predictions/<condition>/<schema>/<model>_seed<seed>.parquet
  - Per-run metrics: results/metrics/v3/<condition>_<schema>_<model>_seed<seed>_metrics.json
  - Aggregate summary: results/metrics/v3/aggregate_summary.json
"""

import os, sys, json, time
from pathlib import Path
import numpy as np
import pandas as pd
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments.pipeline_engine import run_experiment, MODELS_CONFIG

SEEDS = [42, 7, 13, 99, 2024]
STRATEGIES = ["unsw_to_cic", "cic_to_unsw", "time_wise", "pcap_wise", "host_wise"]
SCHEMAS = ["11_features", "20_features"]
MODELS = ["random_forest", "xgboost", "svm", "isolation_forest", "mlp"]

def main():
    total_runs = len(STRATEGIES) * len(SCHEMAS) * len(MODELS) * len(SEEDS)
    print(f"=== Starting Phase 3 Full Rerun: {total_runs} total model runs ===")
    
    start_all = time.time()
    completed = 0
    all_results = []
    
    for strat in STRATEGIES:
        for schema in SCHEMAS:
            print(f"\n--- Strategy: {strat} | Schema: {schema} ---")
            for model_name in MODELS:
                t_model_start = time.time()
                seed_f1s = []
                for seed in SEEDS:
                    completed += 1
                    try:
                        res = run_experiment(strat, schema, model_name, seed)
                        f1 = res["test_metrics"]["f1"]
                        auc = res["test_metrics"]["roc_auc"]
                        seed_f1s.append(f1)
                        all_results.append(res)
                    except Exception as e:
                        print(f"  [ERROR] {strat} | {schema} | {model_name} | Seed {seed}: {e}")
                
                mean_f1 = np.mean(seed_f1s) if seed_f1s else 0.0
                std_f1 = np.std(seed_f1s, ddof=1) if len(seed_f1s) > 1 else 0.0
                elapsed = time.time() - t_model_start
                print(f"  [{completed}/{total_runs}] {model_name:<16}: F1 = {mean_f1:.4f} ± {std_f1:.4f} ({elapsed:.1f}s)")

    # Compute and save aggregate summary
    print("\nCompiling aggregate summary table...")
    agg = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list))))
    
    for r in all_results:
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

    summary_file = ROOT / "results/metrics/v3/aggregate_summary.json"
    with open(summary_file, "w") as f:
        json.dump(summary_table, f, indent=2)
    print(f"Aggregate summary saved to {summary_file}")
    
    total_time = time.time() - start_all
    print(f"\n=== Full Rerun Completed in {total_time:.1f}s ===")

if __name__ == "__main__":
    main()
