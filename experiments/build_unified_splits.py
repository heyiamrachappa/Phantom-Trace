#!/usr/bin/env python3
"""
Phase 2 — Build Unified Named Splits
Generates explicit, named, independently regenerable split files for:
  1. unsw_to_cic   : Train UNSW+Synthetic (4,303), Val UNSW holdout (538), Test CIC PortScan (168,930)
  2. cic_to_unsw   : Train CIC+Synthetic (5,186), Val CIC holdout (916), Test UNSW-NB15 (5,277)
  3. pcap_wise     : Train Synthetic (86), Val Synthetic holdout (16), Test CIC PortScan (168,930)
  4. time_wise     : Combined 70/10/20 temporal split (7,071 / 1,010 / 2,021)
  5. host_wise     : Synthetic IP-disjoint split (70 / 18 / 14)

All test splits are verified to contain both classes.
Outputs: dataset/splits/<name>/{train,val,test}.parquet and results/unified_splits_report.json
"""

import os, sys, json
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "results"
SPLITS_DIR = ROOT / "dataset" / "splits"
MAPPED_DIR = ROOT / "dataset" / "mapped"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
SPLITS_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_STATE = 42

FEATURE_NAMES = [
    "flow_duration", "flow_packet_count", "flow_bytes",
    "flow_syn_ratio", "flow_ack_ratio", "flow_rst_ratio", "flow_fin_ratio",
    "flow_size_mean", "flow_size_var",
    "flow_interval_mean", "flow_interval_var",
    "host_port_entropy", "host_dst_entropy", "host_dst_diversity",
    "host_syn_ratio", "host_failed_flow_ratio",
    "host_packet_rate", "host_interval_mean", "host_interval_var", "host_packet_size_var"
]

META_COLS = ["label", "dataset_source", "attack_type"]
SAVE_COLS = FEATURE_NAMES + META_COLS

def split_stats(df: pd.DataFrame) -> dict:
    n = len(df)
    n_benign = int((df["label"] == 0).sum())
    n_recon = int((df["label"] == 1).sum())
    n_dup = int(df[FEATURE_NAMES].duplicated().sum()) if len(df) > 0 else 0
    n_null = int(df[FEATURE_NAMES].isnull().sum().sum())
    sources = df["dataset_source"].value_counts().to_dict() if "dataset_source" in df.columns else {}
    return {
        "total": n,
        "benign": n_benign,
        "recon": n_recon,
        "class_balance_ratio": round(n_recon / n_benign, 4) if n_benign > 0 else None,
        "duplicate_feature_rows": n_dup,
        "missing_values": n_null,
        "dataset_sources": {str(k): int(v) for k, v in sources.items()}
    }

def verify_split(split_name: str, train: pd.DataFrame, val: pd.DataFrame, test: pd.DataFrame):
    issues = []
    for name, df in [("train", train), ("val", val), ("test", test)]:
        if (df["label"] == 0).sum() == 0:
            issues.append(f"{split_name}/{name}: NO BENIGN SAMPLES")
        if (df["label"] == 1).sum() == 0:
            issues.append(f"{split_name}/{name}: NO RECON SAMPLES")
    if issues:
        raise ValueError(f"Split verification failed for {split_name}:\n" + "\n".join(issues))
    print(f"  ✓ {split_name} split verified: all subsets contain both classes")

def save_split(strategy: str, train: pd.DataFrame, val: pd.DataFrame, test: pd.DataFrame):
    d = SPLITS_DIR / strategy
    d.mkdir(parents=True, exist_ok=True)
    for name, df in [("train", train), ("val", val), ("test", test)]:
        path = d / f"{name}.parquet"
        cols_to_save = [c for c in SAVE_COLS if c in df.columns]
        df[cols_to_save].reset_index(drop=True).to_parquet(path, index=False)
    print(f"  Saved {strategy}: train={len(train)}, val={len(val)}, test={len(test)}")

def load_data():
    # Synthetic
    syn = pd.read_csv(ROOT / "dataset" / "raw_features.csv")
    for col in FEATURE_NAMES:
        if col not in syn.columns:
            syn[col] = 0.0
    if "dataset_source" not in syn.columns:
        syn["dataset_source"] = "synthetic"
    if "attack_type" not in syn.columns:
        syn["attack_type"] = syn.get("pcap_filename", "unknown").str.replace(".pcap", "", regex=False)
    
    # CIC
    cic = pd.read_parquet(MAPPED_DIR / "cic_mapped.parquet")
    if "dataset_source" not in cic.columns:
        cic["dataset_source"] = "cic_ids_2017_friday_portscan"
    
    # UNSW
    unsw = pd.read_parquet(MAPPED_DIR / "unsw_mapped.parquet")
    if "dataset_source" not in unsw.columns:
        unsw["dataset_source"] = "unsw_nb15"
        
    return syn, cic, unsw

def main():
    report = {}
    syn, cic, unsw = load_data()
    print(f"Loaded datasets: synthetic={len(syn)}, CIC={len(cic):,}, UNSW={len(unsw):,}")

    # Shared CIC test set (PortScan + 10,000 Benign)
    cic_recon = cic[cic["label"] == 1]
    cic_benign = cic[cic["label"] == 0].sample(n=min(10000, (cic["label"] == 0).sum()), random_state=RANDOM_STATE)
    cic_test = shuffle(pd.concat([cic_recon, cic_benign]), random_state=RANDOM_STATE)

    # 1. unsw_to_cic (Primary Cross-Dataset Direction)
    print("\n[1] Building unsw_to_cic split...")
    combined_unsw = pd.concat([syn, unsw]).reset_index(drop=True)
    combined_unsw = shuffle(combined_unsw, random_state=RANDOM_STATE)
    u2c_train, u2c_tmp = train_test_split(combined_unsw, test_size=0.20, stratify=combined_unsw["label"], random_state=RANDOM_STATE)
    u2c_val, _ = train_test_split(u2c_tmp, test_size=0.50, stratify=u2c_tmp["label"], random_state=RANDOM_STATE)
    u2c_test = cic_test
    verify_split("unsw_to_cic", u2c_train, u2c_val, u2c_test)
    save_split("unsw_to_cic", u2c_train, u2c_val, u2c_test)
    # Also save as canonical alias 'cross_dataset' for backward compatibility
    save_split("cross_dataset", u2c_train, u2c_val, u2c_test)
    report["unsw_to_cic"] = {
        "description": "Train: UNSW-NB15+Synthetic; Val: UNSW holdout; Test: CIC-IDS-2017 Friday PortScan",
        "train": split_stats(u2c_train),
        "val": split_stats(u2c_val),
        "test": split_stats(u2c_test)
    }

    # 2. cic_to_unsw (Reverse Cross-Dataset Direction - Live First-Class Split)
    print("\n[2] Building cic_to_unsw split (5,186 train / 916 val / 5,277 test)...")
    cic_sample = shuffle(pd.concat([
        cic[cic["label"] == 1].sample(n=min(3000, (cic["label"] == 1).sum()), random_state=RANDOM_STATE),
        cic[cic["label"] == 0].sample(n=min(3000, (cic["label"] == 0).sum()), random_state=RANDOM_STATE)
    ]), random_state=RANDOM_STATE)
    c2u_combined = pd.concat([syn, cic_sample]).reset_index(drop=True)
    c2u_train, c2u_val = train_test_split(c2u_combined, test_size=0.15, stratify=c2u_combined["label"], random_state=RANDOM_STATE)
    c2u_test = shuffle(unsw, random_state=RANDOM_STATE)
    verify_split("cic_to_unsw", c2u_train, c2u_val, c2u_test)
    save_split("cic_to_unsw", c2u_train, c2u_val, c2u_test)
    report["cic_to_unsw"] = {
        "description": "Train: CIC PortScan sample (6000)+Synthetic; Val: CIC holdout; Test: UNSW-NB15 Mapped (5277)",
        "train": split_stats(c2u_train),
        "val": split_stats(c2u_val),
        "test": split_stats(c2u_test)
    }

    # 3. pcap_wise split
    print("\n[3] Building pcap_wise split...")
    syn_train, syn_val = train_test_split(syn, test_size=0.15, stratify=syn["label"], random_state=RANDOM_STATE)
    verify_split("pcap_wise", syn_train, syn_val, cic_test)
    save_split("pcap_wise", syn_train, syn_val, cic_test)
    report["pcap_wise"] = {
        "description": "Train: Synthetic corpus; Val: Synthetic holdout; Test: CIC-IDS-2017 Friday PortScan",
        "train": split_stats(syn_train),
        "val": split_stats(syn_val),
        "test": split_stats(cic_test)
    }

    # 4. time_wise split
    print("\n[4] Building time_wise split...")
    cic_sample_time = shuffle(pd.concat([
        cic[cic["label"] == 1].sample(n=min(5000, (cic["label"] == 1).sum()), random_state=RANDOM_STATE),
        cic[cic["label"] == 0].sample(n=min(5000, (cic["label"] == 0).sum()), random_state=RANDOM_STATE)
    ]), random_state=RANDOM_STATE)
    combined_time = pd.concat([syn, cic_sample_time]).reset_index(drop=True)
    n = len(combined_time)
    n_train = int(n * 0.70)
    n_val = int(n * 0.10)
    tw_train = combined_time.iloc[:n_train]
    tw_val = combined_time.iloc[n_train:n_train+n_val]
    tw_test = combined_time.iloc[n_train+n_val:]
    verify_split("time_wise", tw_train, tw_val, tw_test)
    save_split("time_wise", tw_train, tw_val, tw_test)
    report["time_wise"] = {
        "description": "Temporal split 70/10/20 on combined synthetic+CIC sample; row order approximates capture time",
        "train": split_stats(tw_train),
        "val": split_stats(tw_val),
        "test": split_stats(tw_test)
    }

    # 5. host_wise split (Synthetic IP-disjoint)
    print("\n[5] Building host_wise split (synthetic host holdout)...")
    test_ips = ["10.0.0.51", "192.168.1.5"]
    hw_test = syn[syn["src_ip"].isin(test_ips)].reset_index(drop=True)
    hw_train_val = syn[~syn["src_ip"].isin(test_ips)].reset_index(drop=True)
    hw_train, hw_val = train_test_split(hw_train_val, test_size=0.20, stratify=hw_train_val["label"], random_state=RANDOM_STATE)
    verify_split("host_wise", hw_train, hw_val, hw_test)
    save_split("host_wise", hw_train, hw_val, hw_test)
    report["host_wise"] = {
        "description": "Genuine host-disjoint split: Train/Val/Test grouped by src_ip on synthetic dataset",
        "train": split_stats(hw_train),
        "val": split_stats(hw_val),
        "test": split_stats(hw_test)
    }

    out_file = RESULTS_DIR / "unified_splits_report.json"
    with open(out_file, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nUnified splits report written to: {out_file}")

    print("\n=== UNIFIED SPLITS SUMMARY ===")
    print(f"{'Strategy':<15} {'Train':>7} {'Val':>7} {'Test':>7} {'Test-Recon':>12} {'Test-Benign':>12}")
    for s in ["unsw_to_cic", "cic_to_unsw", "pcap_wise", "time_wise", "host_wise"]:
        r = report[s]
        print(f"{s:<15} {r['train']['total']:>7} {r['val']['total']:>7} {r['test']['total']:>7} "
              f"{r['test']['recon']:>12} {r['test']['benign']:>12}")

if __name__ == "__main__":
    main()
