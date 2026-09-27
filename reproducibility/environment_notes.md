# Environment and Hardware Manifest

- **Operating System**: Linux 6.17.0 x86_64
- **Python Version**: 3.12.3
- **CPU**: 16 logical cores
- **System Memory**: 16.44 GB RAM
- **Key Libraries**:
  - `scikit-learn`: 1.8.0
  - `xgboost`: 3.2.0
  - `shap`: 0.52.0
  - `numpy`: 2.4.6
  - `pandas`: 3.0.3
  - `scipy`: 1.18.0
  - `pyarrow`: 24.0.0
  - `joblib`: 1.5.3

## Reproduction Commands

To reproduce the entire benchmark and generate all artifacts:

1. **Build Unified Splits**:
   ```bash
   python3 experiments/build_unified_splits.py
   ```
2. **Execute Full 5-Seed Benchmark Rerun**:
   ```bash
   python3 experiments/run_full_rerun.py
   ```
3. **Execute Mathematical and Empirical Audits**:
   ```bash
   python3 experiments/audit_isolation_forest.py
   python3 experiments/audit_domain_and_dedup.py
   ```
4. **Compute Redesigned Statistics**:
   ```bash
   python3 experiments/compute_redesigned_statistics.py
   ```
5. **Compile Certified Tables and Confusion Matrices**:
   ```bash
   python3 experiments/compile_tables_and_matrices.py
   ```
6. **Verify Manuscript Text Against Generated Values**:
   ```bash
   python3 experiments/audit_manuscript_values.py
   ```
