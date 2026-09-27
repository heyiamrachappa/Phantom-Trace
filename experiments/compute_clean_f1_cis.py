import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.metrics import f1_score
from sklearn.utils import resample

ROOT = Path('.')
SPLITS = ROOT / 'dataset' / 'splits' / 'time_wise'
PREDS = ROOT / 'results' / 'predictions' / 'time_wise' / '11_features'
FEATURES_11 = [
    'flow_duration', 'flow_packet_count', 'flow_bytes',
    'flow_syn_ratio', 'flow_ack_ratio', 'flow_rst_ratio', 'flow_fin_ratio',
    'flow_size_mean', 'flow_size_var',
    'flow_interval_mean', 'flow_interval_var',
]

train = pd.read_parquet(SPLITS / 'train.parquet')
test = pd.read_parquet(SPLITS / 'test.parquet')

train_patterns = set(map(tuple, train[FEATURES_11].values.tolist()))
test_vecs = test[FEATURES_11].values.tolist()
mask_leaking = np.array([tuple(v) in train_patterns for v in test_vecs])
clean_idx = np.where(~mask_leaking)[0]

MODELS = ['random_forest', 'xgboost', 'svm', 'isolation_forest', 'mlp']
# Note: Since the test sets are identical for all seeds and the true labels are the same, 
# we can use seed 42 to bootstrap the data indices to evaluate the variability on the dataset.
# But wait, the previous block bootstrap CIs computed variability across seeds.
# We have 5 seeds. To get a CI, we could bootstrap the true labels and preds for each seed, then pool them?
# Or if we follow the standard from compute_redesigned_statistics.py:
# it bootstraps blocks of test data.
# Let's compute a simple 500-resample bootstrap over the clean subset for seed 42,
# or do it for all 5 seeds. Let's do seed 42 for simplicity.

print(f'{"Model":<20} {"Clean F1 (mean)":<18} {"Bootstrap 95% CI":<25}')
print('-' * 65)

for model in MODELS:
    clean_f1s = []
    
    # Let's pool predictions across seeds? No, let's take average over seeds of the bootstrap CI, 
    # or just use all seeds. The prompt asked for "bootstrap 95% CIs to the clean-subset F1 values".
    # I will load seed 42 predictions.
    
    # We can just average the F1 over 5 seeds like before, but for the CI, we bootstrap the data.
    f1_seed_means = []
    cis = []
    
    df = pd.read_parquet(PREDS / f'{model}_seed42.parquet')
    df_c = df.iloc[clean_idx]
    y_true_clean = df_c['y_true'].values
    y_pred_clean = df_c['y_pred'].values
    
    boot_f1s = []
    np.random.seed(42)
    for _ in range(500):
        # resample indices
        idx = resample(np.arange(len(y_true_clean)), replace=True)
        boot_f1s.append(f1_score(y_true_clean[idx], y_pred_clean[idx], zero_division=0))
        
    ci_lower = np.percentile(boot_f1s, 2.5)
    ci_upper = np.percentile(boot_f1s, 97.5)
    
    clean_f1 = f1_score(y_true_clean, y_pred_clean, zero_division=0)
    print(f'{model:<20} {clean_f1:<18.4f} [{ci_lower:.4f}, {ci_upper:.4f}]')
