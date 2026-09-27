import os, sys, json, time
from pathlib import Path
import numpy as np
import pandas as pd
from collections import defaultdict

ROOT = Path('.').resolve()
sys.path.insert(0, str(ROOT))

from experiments.pipeline_engine import run_experiment

SEEDS = [42, 7, 13, 99, 2024]
STRATEGIES = ["unsw_to_cic", "cic_to_unsw", "time_wise", "pcap_wise", "host_wise"]
SCHEMAS = ["11_features", "20_features"]
MODELS = ["isolation_forest"]

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
                        seed_f1s.append(f1)
                        all_results.append(res)
                    except Exception as e:
                        print(f"  [ERROR] {strat} | {schema} | {model_name} | Seed {seed}: {e}")
                
                mean_f1 = np.mean(seed_f1s) if seed_f1s else 0.0
                std_f1 = np.std(seed_f1s, ddof=1) if len(seed_f1s) > 1 else 0.0
                elapsed = time.time() - t_model_start
                print(f"  [{completed}/{total_runs}] {model_name:<16}: F1 = {mean_f1:.4f} ± {std_f1:.4f} ({elapsed:.1f}s)")
                
if __name__ == "__main__":
    main()
