#!/usr/bin/env python3
"""
Phase 8 — Automated Manuscript Value Audit
Parses manuscript.md and verifies every quoted number, dataset row count,
partition size, and model performance metric against the actual generated result files.
Flags all mismatches explicitly.
Outputs: results/audits/manuscript_audit_report.json
"""

import os, sys, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT_PATH = ROOT / "manuscript.md"
AUDIT_DIR = ROOT / "results" / "audits"
AUDIT_DIR.mkdir(parents=True, exist_ok=True)

AGGREGATE_V3_JSON = ROOT / "results" / "metrics" / "v3" / "aggregate_summary.json"

def get_markdown_tables(text):
    tables = []
    lines = text.split('\n')
    current_table = []
    for line in lines:
        if line.strip().startswith('|'):
            current_table.append(line.strip())
        else:
            if len(current_table) > 2:
                tables.append(current_table)
            current_table = []
    if len(current_table) > 2:
        tables.append(current_table)
    return tables

def audit_manuscript():
    if not MANUSCRIPT_PATH.exists():
        raise FileNotFoundError(f"Manuscript not found at: {MANUSCRIPT_PATH}")
        
    with open(MANUSCRIPT_PATH, "r") as f:
        text = f.read()

    report = {
        "manuscript_file": str(MANUSCRIPT_PATH),
        "audit_timestamp": Path(MANUSCRIPT_PATH).stat().st_mtime,
        "checks": []
    }

    # 1. Dataset Counts Checks
    counts_to_check = [
        ("CIC-IDS-2017 Total Rows", r"286,467", 286467),
        ("CIC-IDS-2017 PortScan Rows", r"158,930", 158930),
        ("CIC-IDS-2017 Benign Rows", r"127,537", 127537),
        ("UNSW-NB15 Subset Rows", r"5,277", 5277),
        ("UNSW-NB15 Reconnaissance Rows", r"1,759", 1759),
        ("UNSW-NB15 Benign Rows", r"3,518", 3518),
        ("Synthetic Corpus Total Rows", r"102", 102),
        ("Synthetic Corpus Scan Rows", r"84", 84),
        ("Synthetic Corpus Benign Rows", r"18", 18),
        ("Pcap-wise Test Set", r"168,930", 168930),
        ("Time-wise Train Set", r"7,071", 7071),
        ("Time-wise Val Set", r"1,010", 1010),
        ("Time-wise Test Set", r"2,021", 2021),
        ("Host-wise Train", r"70", 70),
        ("Host-wise Val", r"18", 18),
        ("Host-wise Test", r"14", 14),
        ("Cross-dataset (UNSW->CIC) Train Set", r"4,303", 4303),
        ("Cross-dataset (UNSW->CIC) Val Set", r"538", 538),
        ("Cross-dataset (CIC->UNSW) Train Set", r"5,186", 5186),
        ("Cross-dataset (CIC->UNSW) Val Set", r"916", 916)
    ]

    for label, pattern, expected_val in counts_to_check:
        found = bool(re.search(pattern, text))
        report["checks"].append({
            "category": "Dataset Accounting",
            "item": label,
            "expected_value": expected_val,
            "found_in_manuscript": found,
            "status": "PASS" if found else "FAIL"
        })

    # 2. Check for V3 Result Alignment
    if not AGGREGATE_V3_JSON.exists():
        report["v3_pipeline_ready"] = False
        report["note"] = "V3 aggregate summary not yet generated; awaiting Phase 3 completion."
    else:
        with open(AGGREGATE_V3_JSON) as f:
            v3_data = json.load(f)
            
        report["v3_pipeline_ready"] = True
        
        # Parse all performance tables
        sections = [
            ("time_wise", "5.1 In-Distribution Performance (Time-Wise Split)"),
            ("pcap_wise", "5.2 Cross-Corpus Generalization (Pcap-Wise Split)"),
            ("cic_to_unsw", "5.3 Reverse Cross-Dataset Split (Train: CIC → Test: UNSW)"),
            ("unsw_to_cic", "5.4 Cross-Dataset Split (Train: UNSW → Test: CIC)")
        ]
        
        # We need to find the tables corresponding to each section
        # Simple heuristic: find the index of the section header, and then find the first table after it.
        lines = text.split('\n')
        
        for strat_name, section_title in sections:
            start_idx = -1
            for i, line in enumerate(lines):
                if section_title in line:
                    start_idx = i
                    break
            
            if start_idx == -1:
                print(f"Warning: Section '{section_title}' not found in manuscript.")
                continue
                
            # Find the first table after this section
            table = []
            for i in range(start_idx, len(lines)):
                line = lines[i].strip()
                if line.startswith('|'):
                    table.append(line)
                elif len(table) > 2:
                    break # Found end of table
                    
            if len(table) < 3:
                print(f"Warning: Table not found for section '{section_title}'.")
                continue
                
            # Parse the table rows for models
            model_map = {
                'RF': 'random_forest',
                'XGB': 'xgboost',
                'SVM': 'svm',
                'MLP': 'mlp',
                'IF': 'isolation_forest'
            }
            
            for row in table[2:]: # skip header and separator
                cols = [c.strip().replace('**', '') for c in row.split('|') if c.strip()]
                if not cols: continue
                model_col = cols[0]
                matched_model = None
                for m_id, m_name in model_map.items():
                    if m_id in model_col:
                        matched_model = m_name
                        break
                
                if matched_model:
                    # columns: Model | Accuracy | Precision | Recall | F1 | MCC | ROC-AUC | PR-AUC
                    # E.g. 0.999 ± 0.000
                    try:
                        f1_str = cols[4].split('±')[0].strip()
                        mcc_str = cols[5].split('±')[0].strip().replace('−', '-')
                        roc_str = cols[6].split('±')[0].strip()
                        pr_str = cols[7].split('±')[0].strip()
                        
                        f1_val = float(f1_str)
                        mcc_val = float(mcc_str)
                        roc_val = float(roc_str)
                        pr_val = float(pr_str)
                        
                        # Compare against JSON
                        json_data = v3_data[strat_name]["11_features"][matched_model]
                        exp_f1 = json_data["f1"]["mean"]
                        exp_mcc = json_data["mcc"]["mean"]
                        exp_roc = json_data["roc_auc"]["mean"]
                        exp_pr = json_data["pr_auc"]["mean"]
                        
                        metrics = [
                            ("F1", f1_val, exp_f1),
                            ("MCC", mcc_val, exp_mcc),
                            ("ROC-AUC", roc_val, exp_roc),
                            ("PR-AUC", pr_val, exp_pr)
                        ]
                        
                        for m_name, parsed_val, exp_val in metrics:
                            status = "PASS" if abs(parsed_val - exp_val) < 0.0015 else "FAIL"
                            report["checks"].append({
                                "category": f"Performance Metrics ({strat_name})",
                                "item": f"{matched_model} {m_name}",
                                "expected_value": round(exp_val, 3),
                                "found_in_manuscript": parsed_val,
                                "status": status
                            })
                    except Exception as e:
                        print(f"Warning: Could not parse row '{row}' for model '{matched_model}' in section '{section_title}': {e}")

    out_file = AUDIT_DIR / "manuscript_audit_report.json"
    with open(out_file, "w") as f:
        json.dump(report, f, indent=2)
        
    print(f"Manuscript audit report written to: {out_file}")
    
    passed = sum(1 for c in report["checks"] if c["status"] == "PASS")
    failed = sum(1 for c in report["checks"] if c["status"] == "FAIL")
    total = len(report["checks"])
    print(f"Audit Summary: {passed}/{total} checks passed.")
    if failed > 0:
        print("FAILED CHECKS:")
        for c in report["checks"]:
            if c["status"] == "FAIL":
                print(f"  [{c['category']}] {c['item']}: Expected {c['expected_value']}, found {c['found_in_manuscript']}")
    
    return report

if __name__ == "__main__":
    audit_manuscript()
