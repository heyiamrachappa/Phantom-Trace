#!/usr/bin/env python3
"""
Phase 2 & 3 — Unified Pipeline Engine
Single source of truth for:
  - Feature extraction and schema selection (11 common features vs. 20 canonical features)
  - Train-fit-only StandardScaler preprocessing (no data leakage to val/test)
  - Model hyperparameter tuning on validation split only
  - Standardized continuous score and binary decision extraction across all 5 models
  - Saving per-instance predictions (y_true, y_pred, y_prob, raw_score)
  - Computing full evaluation metrics and confusion matrices with zero pending cells
"""

import os, sys, json, time, platform, psutil
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.svm import SVC
from xgboost import XGBClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, matthews_corrcoef, roc_auc_score,
                             average_precision_score, confusion_matrix)
from sklearn.model_selection import ParameterGrid

ROOT = Path(__file__).resolve().parents[1]
SPLITS_DIR = ROOT / "dataset" / "splits"
RESULTS_DIR = ROOT / "results"
PREDICTIONS_DIR = RESULTS_DIR / "predictions"
METRICS_DIR = RESULTS_DIR / "metrics" / "v3"

PREDICTIONS_DIR.mkdir(parents=True, exist_ok=True)
METRICS_DIR.mkdir(parents=True, exist_ok=True)

# 20 canonical features
FEATURES_20 = [
    "flow_duration", "flow_packet_count", "flow_bytes",
    "flow_syn_ratio", "flow_ack_ratio", "flow_rst_ratio", "flow_fin_ratio",
    "flow_size_mean", "flow_size_var",
    "flow_interval_mean", "flow_interval_var",
    "host_port_entropy", "host_dst_entropy", "host_dst_diversity",
    "host_syn_ratio", "host_failed_flow_ratio",
    "host_packet_rate", "host_interval_mean", "host_interval_var", "host_packet_size_var"
]

# 11 strictly common flow-level features (Primary baseline)
FEATURES_11 = FEATURES_20[:11]

MODELS_CONFIG = {
    "random_forest": {
        "cls": RandomForestClassifier,
        "grid": {"n_estimators": [100, 200], "max_depth": [None, 15]},
        "params_fixed": {"random_state": None, "class_weight": "balanced", "n_jobs": -1},
        "needs_scaling": False
    },
    "xgboost": {
        "cls": XGBClassifier,
        "grid": {"max_depth": [5, 7], "learning_rate": [0.1, 0.05]},
        "params_fixed": {"objective": "binary:logistic", "eval_metric": "logloss", "random_state": None, "n_jobs": -1},
        "needs_scaling": False
    },
    "svm": {
        "cls": SVC,
        "grid": {"C": [1.0, 5.0], "kernel": ["rbf"]},
        "params_fixed": {"probability": True, "random_state": None},
        "needs_scaling": True
    },
    "isolation_forest": {
        "cls": IsolationForest,
        "grid": {"contamination": [0.1]},
        "params_fixed": {"random_state": None, "n_jobs": -1},
        "needs_scaling": False
    },
    "mlp": {
        "cls": MLPClassifier,
        "grid": {"hidden_layer_sizes": [(100,), (200,)], "alpha": [1e-4]},
        "params_fixed": {"max_iter": 200, "random_state": None},
        "needs_scaling": True
    }
}

def load_split(strategy: str, split_name: str) -> pd.DataFrame:
    path = SPLITS_DIR / strategy / f"{split_name}.parquet"
    if not path.exists():
        raise FileNotFoundError(f"Split file missing: {path}")
    return pd.read_parquet(path)

def scale_datasets(X_train, X_val, X_test, feature_names):
    """Fits StandardScaler ONLY on train, transforms val and test."""
    scaler = StandardScaler()
    X_train_s = pd.DataFrame(scaler.fit_transform(X_train[feature_names]), columns=feature_names, index=X_train.index)
    X_val_s = pd.DataFrame(scaler.transform(X_val[feature_names]), columns=feature_names, index=X_val.index)
    X_test_s = pd.DataFrame(scaler.transform(X_test[feature_names]), columns=feature_names, index=X_test.index)
    return X_train_s, X_val_s, X_test_s, scaler

def predict_model(model, model_name: str, X):
    """
    Standardizes predictions and continuous scores.
    Returns: (binary_pred, continuous_prob, raw_score)
    """
    if model_name in ["random_forest", "xgboost", "mlp"]:
        probs = model.predict_proba(X)[:, 1]
        preds = (probs >= 0.5).astype(int)
        raw_scores = probs
    elif model_name == "svm":
        probs = model.predict_proba(X)[:, 1]
        preds = (probs >= 0.5).astype(int)
        raw_scores = model.decision_function(X)
    elif model_name == "isolation_forest":
        raw_df = model.decision_function(X)
        # Dynamic orientation and threshold determined during validation
        orientation = getattr(model, '_IF_ORIENTATION', -1)
        thresh = getattr(model, '_IF_THRESHOLD', 0.0)
        
        # Raw anomaly score: higher means more recon
        raw_scores = raw_df * orientation
        
        # Centered logistic mapping so raw_scores=thresh maps to prob=0.5
        probs = 1.0 / (1.0 + np.exp(-(raw_scores - thresh)))
        preds = (probs >= 0.5).astype(int)
    else:
        preds = model.predict(X)
        probs = preds.astype(float)
        raw_scores = probs
    return preds, probs, raw_scores

def evaluate_predictions(y_true, y_pred, y_prob, raw_score=None):
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()
    
    unique_classes = len(np.unique(y_true))
    roc_auc = roc_auc_score(y_true, y_prob) if unique_classes > 1 else None
    pr_auc = average_precision_score(y_true, y_prob) if unique_classes > 1 else None
    
    # Also record raw score ROC-AUC for audit verification
    roc_auc_raw = roc_auc_score(y_true, raw_score) if (raw_score is not None and unique_classes > 1) else None
    
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "mcc": float(matthews_corrcoef(y_true, y_pred)),
        "roc_auc": float(roc_auc) if roc_auc is not None else None,
        "pr_auc": float(pr_auc) if pr_auc is not None else None,
        "roc_auc_raw_score": float(roc_auc_raw) if roc_auc_raw is not None else None,
        "prevalence": float(np.mean(y_true)),
        "confusion_matrix": {
            "tn": int(tn),
            "fp": int(fp),
            "fn": int(fn),
            "tp": int(tp),
            "matrix": [[int(tn), int(fp)], [int(fn), int(tp)]]
        }
    }

def tune_and_train_model(model_name: str, X_train, y_train, X_val, y_val, seed: int):
    cfg = MODELS_CONFIG[model_name]
    Cls = cfg["cls"]
    grid = list(ParameterGrid(cfg["grid"]))
    best_score = -np.inf
    best_model = None
    best_params = None

    for params in grid:
        fixed = cfg["params_fixed"].copy()
        fixed.update(params)
        fixed["random_state"] = seed
        model = Cls(**fixed)
        model.fit(X_train, y_train)
        
        if model_name == "isolation_forest":
            raw_train = model.decision_function(X_train)
            mean_raw_b = raw_train[y_train==0].mean()
            mean_raw_r = raw_train[y_train==1].mean()
            orientation = 1 if mean_raw_r > mean_raw_b else -1
            model._IF_ORIENTATION = orientation
            
            raw_val = model.decision_function(X_val) * orientation
            best_th = 0.0
            best_th_f1 = -1
            min_val, max_val = raw_val.min(), raw_val.max()
            for th in np.linspace(min_val, max_val, 100):
                preds_val = (raw_val >= th).astype(int)
                f1 = f1_score(y_val, preds_val, zero_division=0)
                if f1 > best_th_f1:
                    best_th_f1 = f1
                    best_th = th
            model._IF_THRESHOLD = best_th
            
        val_pred, val_prob, _ = predict_model(model, model_name, X_val)
        val_f1 = f1_score(y_val, val_pred, zero_division=0)
        
        if val_f1 > best_score:
            best_score = val_f1
            best_model = model
            best_params = fixed

    return best_model, best_params, best_score

def run_experiment(strategy: str, schema_name: str, model_name: str, seed: int):
    features = FEATURES_11 if schema_name == "11_features" else FEATURES_20
    needs_scaling = MODELS_CONFIG[model_name]["needs_scaling"]

    # 1. Load data
    train_df = load_split(strategy, "train")
    val_df = load_split(strategy, "val")
    test_df = load_split(strategy, "test")

    y_train = train_df["label"].values
    y_val = val_df["label"].values
    y_test = test_df["label"].values

    # 2. Preprocess / Scale
    if needs_scaling:
        X_train, X_val, X_test, _ = scale_datasets(train_df, val_df, test_df, features)
    else:
        X_train = train_df[features].copy()
        X_val = val_df[features].copy()
        X_test = test_df[features].copy()

    # 3. Train & Tune
    t0 = time.time()
    best_model, best_params, best_val_f1 = tune_and_train_model(model_name, X_train, y_train, X_val, y_val, seed)
    train_time = time.time() - t0

    # 4. Predict on Test
    t1 = time.time()
    test_pred, test_prob, test_raw = predict_model(best_model, model_name, X_test)
    predict_time = time.time() - t1

    # 5. Evaluate Metrics
    metrics = evaluate_predictions(y_test, test_pred, test_prob, test_raw)

    # 6. Save per-instance predictions (Phase 3 requirement)
    pred_dir = PREDICTIONS_DIR / strategy / schema_name
    pred_dir.mkdir(parents=True, exist_ok=True)
    pred_path = pred_dir / f"{model_name}_seed{seed}.parquet"
    
    pred_df = pd.DataFrame({
        "y_true": y_test,
        "y_pred": test_pred,
        "y_prob": test_prob,
        "raw_score": test_raw
    })
    pred_df.to_parquet(pred_path, index=False)

    # 7. Save run metrics JSON
    meta = {
        "strategy": strategy,
        "schema": schema_name,
        "features_used": features,
        "features_count": len(features),
        "model": model_name,
        "seed": seed,
        "train_time_sec": round(train_time, 4),
        "predict_time_sec": round(predict_time, 4),
        "hyperparameters": best_params,
        "validation_f1": float(best_val_f1),
        "test_metrics": metrics,
        "system_info": {
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(logical=True),
            "ram_gb": round(psutil.virtual_memory().total / 1e9, 2)
        }
    }
    
    json_path = METRICS_DIR / f"{strategy}_{schema_name}_{model_name}_seed{seed}_metrics.json"
    with open(json_path, "w") as f:
        json.dump(meta, f, indent=2)

    return meta

if __name__ == "__main__":
    print("Unified Pipeline Engine ready.")
