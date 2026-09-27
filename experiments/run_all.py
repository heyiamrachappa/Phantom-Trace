#!/usr/bin/env python3
"""
Phase 8 — Master End-to-End Benchmark Execution and Reproduction Runner
Executes all steps in sequence:
  1. Data Accounting
  2. Split Generation
  3. 5-Seed Benchmark Rerun (with saved per-instance predictions)
  4. Audits (IF semantics, domain classifier, dedup sensitivity, matched downsampling)
  5. Redesigned Statistics (clustered bootstrap CIs, Holm correction, Cliff's delta)
  6. Table and Confusion Matrix Compilation
  7. Automated Manuscript Text Audit
"""

import os, sys, time, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STEPS = [
    ("Phase 1: Master Data Accounting", [sys.executable, str(ROOT / "experiments/comprehensive_data_accounting.py")]),
    ("Phase 2: Build Unified Named Splits", [sys.executable, str(ROOT / "experiments/build_unified_splits.py")]),
    ("Phase 3: Full 5-Seed Rerun with Saved Predictions", [sys.executable, str(ROOT / "experiments/run_full_rerun.py")]),
    ("Phase 4A: Isolation Forest Semantics Audit", [sys.executable, str(ROOT / "experiments/audit_isolation_forest.py")]),
    ("Phase 4B: Domain and Deduplication Audit", [sys.executable, str(ROOT / "experiments/audit_domain_and_dedup.py")]),
    ("Phase 5: Redesigned Statistical Analysis", [sys.executable, str(ROOT / "experiments/compute_redesigned_statistics.py")]),
    ("Phases 6 & 7: Compile Tables and Confusion Matrices", [sys.executable, str(ROOT / "experiments/compile_tables_and_matrices.py")]),
    ("Phase 8: Automated Manuscript Value Audit", [sys.executable, str(ROOT / "experiments/audit_manuscript_values.py")]),
]

def main():
    print("=================================================================")
    print("      PhantomTrace: Master End-to-End Evaluation Pipeline       ")
    print("=================================================================\n")
    
    total_start = time.time()
    for name, cmd in STEPS:
        print(f"\n>>> Running: {name}")
        t0 = time.time()
        res = subprocess.run(cmd, cwd=str(ROOT))
        if res.returncode != 0:
            print(f"\n[FATAL] Step '{name}' failed with return code {res.returncode}")
            sys.exit(res.returncode)
        print(f">>> Completed '{name}' in {time.time() - t0:.1f}s")
        
    print(f"\n=================================================================")
    print(f"  All phases successfully completed in {time.time() - total_start:.1f}s")
    print(f"=================================================================")

if __name__ == "__main__":
    main()
