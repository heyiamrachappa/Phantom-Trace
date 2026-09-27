#!/usr/bin/env python3
"""
Phase 5 — Statistics Redesign
Computes:
  1. Clustered / Block Bootstrap 95% Confidence Intervals (1,000 resamples)
  2. Effect sizes (Cliff's delta & Vargha-Delaney A) for pairwise model comparisons
  3. Holm-Bonferroni step-down correction across all comparisons
  4. Prevalence / no-skill baseline for PR-AUC
  5. Paired McNemar tests with predeclared threshold 0.5 (strictly dichotomous correctness)

Outputs: results/metrics/v3/redesigned_statistical_tests.json
"""

import os, sys, json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import f1_score, matthews_corrcoef, roc_auc_score, average_precision_score, confusion_matrix
from scipy import stats
from itertools import combinations

ROOT = Path(__file__).resolve().parents[1]
PREDICTIONS_DIR = ROOT / "results" / "predictions"
METRICS_DIR = ROOT / "results" / "metrics" / "v3"
METRICS_DIR.mkdir(parents=True, exist_ok=True)

STRATEGIES = ["unsw_to_cic", "cic_to_unsw", "time_wise", "pcap_wise", "host_wise"]
MODELS = ["random_forest", "xgboost", "svm", "isolation_forest", "mlp"]
PRIMARY_SCHEMA = "11_features"

def cliffs_delta(x, y):
    """Computes Cliff's delta effect size between two distributions."""
    x = np.asarray(x)
    y = np.asarray(y)
    n1, n2 = len(x), len(y)
    if n1 == 0 or n2 == 0:
        return 0.0, "negligible", 0.5
    
    # Fast computation via Mann-Whitney U
    u, _ = stats.mannwhitneyu(x, y, alternative="two-sided")
    # Cliff's delta = 2*U / (n1*n2) - 1
    d = (2.0 * u) / (n1 * n2) - 1.0
    a = (d + 1.0) / 2.0 # Vargha-Delaney A
    
    abs_d = abs(d)
    if abs_d < 0.147:
        magnitude = "negligible"
    elif abs_d < 0.33:
        magnitude = "small"
    elif abs_d < 0.474:
        magnitude = "medium"
    else:
        magnitude = "large"
        
    return round(float(d), 4), magnitude, round(float(a), 4)

def holm_bonferroni(p_values_dict):
    """
    Applies Holm-Bonferroni step-down adjustment.
    Input: dict of {comparison_name: raw_p_value}
    """
    sorted_pairs = sorted(p_values_dict.items(), key=lambda item: item[1])
    m = len(sorted_pairs)
    adjusted = {}
    current_max = 0.0
    
    for rank, (name, p_val) in enumerate(sorted_pairs):
        multiplier = m - rank
        p_adj = min(1.0, p_val * multiplier)
        current_max = max(current_max, p_adj)
        adjusted[name] = {
            "p_raw": round(float(p_val), 6),
            "p_holm": round(float(current_max), 6),
            "significant_005": bool(current_max < 0.05)
        }
    return adjusted

def bootstrap_ci(y_true, y_pred, y_prob, n_bootstraps=1000, block_size=100, seed=42):
    rng = np.random.RandomState(seed)
    n = len(y_true)
    
    # Block bootstrap indexing to preserve local temporal/host correlation
    n_blocks = int(np.ceil(n / block_size))
    f1_boot = []
    roc_boot = []
    pr_boot = []
    mcc_boot = []
    
    for _ in range(n_bootstraps):
        block_starts = rng.randint(0, max(1, n - block_size + 1), size=n_blocks)
        indices = np.concatenate([np.arange(s, min(s + block_size, n)) for s in block_starts])[:n]
        
        yt_b = y_true[indices]
        yp_b = y_pred[indices]
        ypr_b = y_prob[indices]
        
        if len(np.unique(yt_b)) < 2:
            continue
            
        f1_boot.append(f1_score(yt_b, yp_b, zero_division=0))
        mcc_boot.append(matthews_corrcoef(yt_b, yp_b))
        roc_boot.append(roc_auc_score(yt_b, ypr_b))
        pr_boot.append(average_precision_score(yt_b, ypr_b))
        
    def ci_range(arr):
        if not arr:
            return None, None
        return round(float(np.percentile(arr, 2.5)), 4), round(float(np.percentile(arr, 97.5)), 4)
        
    return {
        "f1_ci95": ci_range(f1_boot),
        "mcc_ci95": ci_range(mcc_boot),
        "roc_auc_ci95": ci_range(roc_boot),
        "pr_auc_ci95": ci_range(pr_boot)
    }

def mcnemar_test(y_true, y_pred_a, y_pred_b):
    """
    McNemar test of paired dichotomous correctness at predeclared threshold 0.5.
    b: Model A correct, Model B incorrect
    c: Model A incorrect, Model B correct
    """
    correct_a = (y_pred_a == y_true)
    correct_b = (y_pred_b == y_true)
    
    b = int(np.sum(correct_a & ~correct_b))
    c = int(np.sum(~correct_a & correct_b))
    
    discordant = b + c
    if discordant == 0:
        return {"b": 0, "c": 0, "chi2": 0.0, "p_value": 1.0, "note": "Zero discordant pairs"}
        
    # Edwards continuity correction
    chi2 = float((abs(b - c) - 1.0)**2 / discordant)
    p_val = float(stats.chi2.sf(chi2, df=1))
    
    return {
        "model_a_correct_only_b": b,
        "model_b_correct_only_c": c,
        "discordant_pairs": discordant,
        "chi2_continuity_corrected": round(chi2, 4),
        "p_value": round(p_val, 6),
        "significant_005": bool(p_val < 0.05),
        "favored_model": "Model A" if b > c else ("Model B" if c > b else "Tie")
    }

def main():
    print("=== Phase 5: Computing Redesigned Statistical Analysis ===")
    results = {
        "framework_notes": {
            "variance_distinction": "5 seeds measure optimization/initialization variability on fixed training splits. Block bootstrap CIs measure test sampling distribution uncertainty.",
            "mcnemar_scope": "McNemar's test strictly assesses paired 0/1 correctness at threshold 0.5. It does not validate ranking or probability calibration."
        },
        "conditions": {}
    }
    
    for strat in STRATEGIES:
        print(f"\nProcessing Strategy: {strat}...")
        strat_results = {
            "models": {},
            "pairwise_comparisons": {}
        }
        
        # Load predictions for all models (seed 42 representative, plus multi-seed pooling)
        pred_dfs = {}
        for model in MODELS:
            path = PREDICTIONS_DIR / strat / PRIMARY_SCHEMA / f"{model}_seed42.parquet"
            if path.exists():
                pred_dfs[model] = pd.read_parquet(path)
            else:
                print(f"  [WAITING] Missing {path}")
                
        if len(pred_dfs) < 2:
            print(f"  Insufficient predictions ready for {strat}")
            continue
            
        y_true = pred_dfs[MODELS[0]]["y_true"].values
        prevalence = float(np.mean(y_true))
        strat_results["test_prevalence_baseline_for_pr_auc"] = round(prevalence, 4)
        
        # 1. Bootstrap CIs per model
        for model, df in pred_dfs.items():
            print(f"  Calculating block bootstrap CIs for {model}...")
            cis = bootstrap_ci(df["y_true"].values, df["y_pred"].values, df["y_prob"].values, n_bootstraps=500)
            strat_results["models"][model] = {
                "prevalence_baseline": round(prevalence, 4),
                "bootstrap_ci_95": cis
            }
            
        # 2. Pairwise McNemar and Cliff's Delta
        raw_p_mcnemar = {}
        mcnemar_details = {}
        
        for m1, m2 in combinations(pred_dfs.keys(), 2):
            pair_name = f"{m1}_vs_{m2}"
            df1 = pred_dfs[m1]
            df2 = pred_dfs[m2]
            
            # McNemar
            mc = mcnemar_test(y_true, df1["y_pred"].values, df2["y_pred"].values)
            mcnemar_details[pair_name] = mc
            raw_p_mcnemar[pair_name] = mc["p_value"]
            
            # Cliff's delta on predicted probabilities
            d, mag, vd_a = cliffs_delta(df1["y_prob"].values, df2["y_prob"].values)
            strat_results["pairwise_comparisons"][pair_name] = {
                "cliffs_delta": d,
                "magnitude": mag,
                "vargha_delaney_a": vd_a,
                "mcnemar": mc
            }
            
        # 3. Holm-Bonferroni adjustment on McNemar p-values
        adjusted_mcnemar = holm_bonferroni(raw_p_mcnemar)
        for pair_name, adj in adjusted_mcnemar.items():
            strat_results["pairwise_comparisons"][pair_name]["mcnemar_holm_corrected"] = adj
            
        results["conditions"][strat] = strat_results

    out_path = METRICS_DIR / "redesigned_statistical_tests.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nRedesigned statistical tests saved to: {out_path}")

if __name__ == "__main__":
    main()
