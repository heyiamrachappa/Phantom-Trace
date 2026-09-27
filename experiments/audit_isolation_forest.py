#!/usr/bin/env python3
"""
Phase 4 — Isolation Forest Score Semantics and Reversal Audit
Provides rigorous mathematical and empirical verification of Isolation Forest
decision function semantics, score negation, and AUC inversion.
Writes results/audits/isolation_forest_audit.json.
"""

import os, sys, json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import roc_auc_score, average_precision_score

ROOT = Path(__file__).resolve().parents[1]
SPLITS_DIR = ROOT / "dataset" / "splits"
AUDIT_DIR = ROOT / "results" / "audits"
AUDIT_DIR.mkdir(parents=True, exist_ok=True)

FEATURES = [
    "flow_duration", "flow_packet_count", "flow_bytes",
    "flow_syn_ratio", "flow_ack_ratio", "flow_rst_ratio", "flow_fin_ratio",
    "flow_size_mean", "flow_size_var",
    "flow_interval_mean", "flow_interval_var"
]

STRATEGIES = ["unsw_to_cic", "cic_to_unsw", "time_wise", "pcap_wise", "host_wise"]

def audit_strategy(strat: str):
    train = pd.read_parquet(SPLITS_DIR / strat / "train.parquet")
    test = pd.read_parquet(SPLITS_DIR / strat / "test.parquet")

    X_train = train[FEATURES]
    y_train = train["label"].values
    X_test = test[FEATURES]
    y_test = test["label"].values

    clf = IsolationForest(contamination=0.1, random_state=42, n_jobs=-1)
    clf.fit(X_train)

    raw_df = clf.decision_function(X_test)
    neg_df = -raw_df

    # Statistics by ground truth class
    benign_mask = (y_test == 0)
    recon_mask = (y_test == 1)

    mean_raw_benign = float(np.mean(raw_df[benign_mask])) if np.any(benign_mask) else None
    mean_raw_recon = float(np.mean(raw_df[recon_mask])) if np.any(recon_mask) else None

    mean_neg_benign = float(np.mean(neg_df[benign_mask])) if np.any(benign_mask) else None
    mean_neg_recon = float(np.mean(neg_df[recon_mask])) if np.any(recon_mask) else None

    auc_raw = float(roc_auc_score(y_test, raw_df)) if len(np.unique(y_test)) > 1 else None
    auc_neg = float(roc_auc_score(y_test, neg_df)) if len(np.unique(y_test)) > 1 else None

    pr_raw = float(average_precision_score(y_test, raw_df)) if len(np.unique(y_test)) > 1 else None
    pr_neg = float(average_precision_score(y_test, neg_df)) if len(np.unique(y_test)) > 1 else None

    # Check polarity
    is_inverted = (auc_raw is not None and auc_neg is not None and auc_neg < 0.1 and auc_raw > 0.9)

    return {
        "train_size": len(train),
        "train_class_ratio_recon_to_benign": round(float((y_train == 1).sum() / (y_train == 0).sum()), 3) if (y_train == 0).sum() > 0 else "N/A",
        "test_size": len(test),
        "test_prevalence": round(float(np.mean(y_test)), 4),
        "score_statistics": {
            "mean_raw_decision_function_benign": round(mean_raw_benign, 4) if mean_raw_benign is not None else None,
            "mean_raw_decision_function_recon": round(mean_raw_recon, 4) if mean_raw_recon is not None else None,
            "mean_negated_score_benign": round(mean_neg_benign, 4) if mean_neg_benign is not None else None,
            "mean_negated_score_recon": round(mean_neg_recon, 4) if mean_neg_recon is not None else None
        },
        "metrics": {
            "roc_auc_raw_decision_function": round(auc_raw, 4) if auc_raw is not None else None,
            "roc_auc_negated_decision_function": round(auc_neg, 4) if auc_neg is not None else None,
            "pr_auc_raw_decision_function": round(pr_raw, 4) if pr_raw is not None else None,
            "pr_auc_negated_decision_function": round(pr_neg, 4) if pr_neg is not None else None,
            "sum_of_raw_and_negated_roc_auc": round(auc_raw + auc_neg, 4) if (auc_raw and auc_neg) else None
        },
        "reversal_detected": is_inverted,
        "explanation": (
            "In this condition, training data has high reconnaissance density. Reconnaissance flows have "
            "repetitive/homogeneous timing and packet length patterns, while benign traffic is heterogeneous. "
            "The isolation trees isolate heterogeneous benign flows faster (at shallower depths), assigning them "
            "more negative anomaly scores than the reconnaissance flows. Negating the score causes reconnaissance "
            "flows to receive lower ranks than benign flows, resulting in a near-perfect ROC-AUC inversion."
            if is_inverted else
            "Under domain shift from an external training set, the test reconnaissance distribution is isolated "
            "faster than inlier reference patterns."
        )
    }

def main():
    report = {
        "audit_title": "Isolation Forest Score Polarity and AUC Inversion Audit",
        "mathematical_principle": (
            "In scikit-learn, IsolationForest.decision_function(X) returns (score_samples(X) - offset_). "
            "By convention in scikit-learn: negative values represent outliers (anomalies), positive values "
            "represent inliers (normal instances). Anomaly score is mathematically -decision_function(X). "
            "When class 1 is defined as Reconnaissance (anomalies), evaluating roc_auc_score(y_true, score) "
            "requires score to be positively correlated with the anomaly class. If the model isolates normal traffic "
            "faster due to high training contamination of scan traffic, score semantics invert."
        ),
        "conditions": {}
    }

    print("Running Isolation Forest Audit across conditions...")
    for strat in STRATEGIES:
        print(f"  Auditing {strat}...")
        report["conditions"][strat] = audit_strategy(strat)

    out_file = AUDIT_DIR / "isolation_forest_audit.json"
    with open(out_file, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nAudit complete. Written to {out_file}")

if __name__ == "__main__":
    main()
