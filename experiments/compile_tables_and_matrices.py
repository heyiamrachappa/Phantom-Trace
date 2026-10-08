#!/usr/bin/env python3
"""
Phases 6 & 7 — Compile Primary 11-Feature Tables and Complete Confusion Matrices
Produces:
  1. Complete Confusion Matrices for EVERY condition, model, and seed directly
     from saved per-instance predictions (ZERO pending/absent cells).
  2. Primary 11-feature cross-dataset and in-distribution benchmark tables.
  3. 20-feature zero-filled schema sensitivity analysis table.

Outputs:
  - results/metrics/v3/full_confusion_matrices.json
  - results/metrics/v3/compiled_benchmark_tables.md
"""

import os, sys, json
from pathlib import Path
import numpy as np
import pandas as pd
from collections import defaultdict
from sklearn.metrics import confusion_matrix

ROOT = Path(__file__).resolve().parents[1]
PREDICTIONS_DIR = ROOT / "results" / "predictions"
METRICS_DIR = ROOT / "results" / "metrics" / "v3"
AGGREGATE_JSON = METRICS_DIR / "aggregate_summary.json"

STRATEGIES = ["unsw_to_cic", "cic_to_unsw", "time_wise", "pcap_wise", "host_wise"]
SCHEMAS = ["11_features", "20_features"]
MODELS = ["random_forest", "xgboost", "svm", "isolation_forest", "mlp"]
SEEDS = [42, 7, 13, 99, 2024]

def compile_confusion_matrices():
    print("Extracting complete confusion matrices from saved predictions...")
    all_cm = {}
    
    for strat in STRATEGIES:
        all_cm[strat] = {}
        for schema in SCHEMAS:
            all_cm[strat][schema] = {}
            for model in MODELS:
                all_cm[strat][schema][model] = {
                    "seeds": {},
                    "aggregate": {}
                }
                
                tns, fps, fns, tps = [], [], [], []
                
                for seed in SEEDS:
                    pred_path = PREDICTIONS_DIR / strat / schema / f"{model}_seed{seed}.parquet"
                    if not pred_path.exists():
                        raise FileNotFoundError(f"Missing prediction file: {pred_path}")
                        
                    df = pd.read_parquet(pred_path)
                    cm = confusion_matrix(df["y_true"], df["y_pred"], labels=[0, 1])
                    tn, fp, fn, tp = cm.ravel()
                    
                    # Verify total equality
                    assert (tn + fp + fn + tp) == len(df), f"CM sum mismatch on {pred_path}"
                    
                    tns.append(tn)
                    fps.append(fp)
                    fns.append(fn)
                    tps.append(tp)
                    
                    all_cm[strat][schema][model]["seeds"][str(seed)] = {
                        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
                        "matrix": [[int(tn), int(fp)], [int(fn), int(tp)]]
                    }
                    
                all_cm[strat][schema][model]["aggregate"] = {
                    "tn_mean": round(float(np.mean(tns)), 1), "tn_std": round(float(np.std(tns, ddof=1)), 1),
                    "fp_mean": round(float(np.mean(fps)), 1), "fp_std": round(float(np.std(fps, ddof=1)), 1),
                    "fn_mean": round(float(np.mean(fns)), 1), "fn_std": round(float(np.std(fns, ddof=1)), 1),
                    "tp_mean": round(float(np.mean(tps)), 1), "tp_std": round(float(np.std(tps, ddof=1)), 1),
                    "mean_matrix": [
                        [round(float(np.mean(tns)), 1), round(float(np.mean(fps)), 1)],
                        [round(float(np.mean(fns)), 1), round(float(np.mean(tps)), 1)]
                    ]
                }
                
    cm_file = METRICS_DIR / "full_confusion_matrices.json"
    with open(cm_file, "w") as f:
        json.dump(all_cm, f, indent=2)
    print(f"Confusion matrices saved: {cm_file}")
    return all_cm

def format_table(agg_data, strat: str, schema: str):
    lines = []
    lines.append(f"| Model | Accuracy | Precision | Recall | F1 | MCC | ROC-AUC | PR-AUC | Prev. Baseline |")
    lines.append(f"|---|---|---|---|---|---|---|---|---|")
    
    model_labels = {
        "random_forest": "Random Forest (RF)",
        "xgboost": "XGBoost (XGB)",
        "svm": "Support Vector Machine (SVM)",
        "isolation_forest": "Isolation Forest (IF)",
        "mlp": "Multi-Layer Perceptron (MLP)"
    }
    
    for m in MODELS:
        md = agg_data[strat][schema][m]
        name = model_labels.get(m, m)
        acc = f"{md['accuracy']['mean']:.3f} ± {md['accuracy']['std']:.3f}"
        prec = f"{md['precision']['mean']:.3f} ± {md['precision']['std']:.3f}"
        rec = f"{md['recall']['mean']:.3f} ± {md['recall']['std']:.3f}"
        f1 = f"{md['f1']['mean']:.3f} ± {md['f1']['std']:.3f}"
        mcc = f"{md['mcc']['mean']:.3f} ± {md['mcc']['std']:.3f}"
        roc = f"{md['roc_auc']['mean']:.3f} ± {md['roc_auc']['std']:.3f}" if md['roc_auc']['mean'] is not None else "N/A"
        pr = f"{md['pr_auc']['mean']:.3f} ± {md['pr_auc']['std']:.3f}" if md['pr_auc']['mean'] is not None else "N/A"
        prev = f"{md['prevalence']['mean']:.3f}"
        lines.append(f"| {name} | {acc} | {prec} | {rec} | {f1} | {mcc} | {roc} | {pr} | {prev} |")
        
    return "\n".join(lines)

def build_markdown_report(all_cm):
    if not AGGREGATE_JSON.exists():
        raise FileNotFoundError(f"Missing {AGGREGATE_JSON}")
        
    with open(AGGREGATE_JSON) as f:
        agg = json.load(f)
        
    doc = []
    doc.append("# Compiled Benchmark Tables and Confusion Matrices\n")
    doc.append("Generated strictly from saved per-instance predictions across 5 random seeds (42, 7, 13, 99, 2024).\n")
    
    doc.append("## 1. Primary Benchmark: 11 Common Flow Features (Zero Host-Leakage)\n")
    
    doc.append("### 1.1 In-Distribution Holdout (`time_wise`)")
    doc.append(format_table(agg, "time_wise", "11_features"))
    doc.append("\n")
    
    doc.append("### 1.2 Synthetic-to-Real Transfer (`pcap_wise`)")
    doc.append(format_table(agg, "pcap_wise", "11_features"))
    doc.append("\n")
    
    doc.append("### 1.3 Host-Disjoint Holdout (`host_wise`)")
    doc.append(format_table(agg, "host_wise", "11_features"))
    doc.append("\n")
    
    doc.append("### 1.4 Primary Cross-Dataset Transfer: UNSW → CIC (`unsw_to_cic`)")
    doc.append(format_table(agg, "unsw_to_cic", "11_features"))
    doc.append("\n")
    
    doc.append("### 1.5 Reverse Cross-Dataset Transfer: CIC → UNSW (`cic_to_unsw`)")
    doc.append(format_table(agg, "cic_to_unsw", "11_features"))
    doc.append("\n")
    
    doc.append("## 2. Sensitivity Analysis: 20-Feature Schema (9 Imputed Host Features)\n")
    
    doc.append("### 2.1 UNSW → CIC (20 Features)")
    doc.append(format_table(agg, "unsw_to_cic", "20_features"))
    doc.append("\n")
    
    doc.append("### 2.2 CIC → UNSW (20 Features)")
    doc.append(format_table(agg, "cic_to_unsw", "20_features"))
    doc.append("\n")
    
    doc.append("## 3. Complete Confusion Matrix Summary (11-Feature Primary Baseline)\n")
    doc.append("| Strategy | Model | True Negative (TN) | False Positive (FP) | False Negative (FN) | True Positive (TP) | Total Test N |")
    doc.append("|---|---|---|---|---|---|---|")
    
    for strat in STRATEGIES:
        for m in MODELS:
            cmd = all_cm[strat]["11_features"][m]["aggregate"]
            tn = f"{cmd['tn_mean']:.0f} ± {cmd['tn_std']:.1f}"
            fp = f"{cmd['fp_mean']:.0f} ± {cmd['fp_std']:.1f}"
            fn = f"{cmd['fn_mean']:.0f} ± {cmd['fn_std']:.1f}"
            tp = f"{cmd['tp_mean']:.0f} ± {cmd['tp_std']:.1f}"
            tot = int(cmd['tn_mean'] + cmd['fp_mean'] + cmd['fn_mean'] + cmd['tp_mean'])
            doc.append(f"| {strat} | {m} | {tn} | {fp} | {fn} | {tp} | {tot:,} |")
            
    out_md = METRICS_DIR / "compiled_benchmark_tables.md"
    with open(out_md, "w") as f:
        f.write("\n".join(doc))
    print(f"Compiled markdown tables saved: {out_md}")

def main():
    cm = compile_confusion_matrices()
    build_markdown_report(cm)

if __name__ == "__main__":
    main()
