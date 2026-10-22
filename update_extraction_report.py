import json

report = """# PhantomTrace Revision: Step 1 Complete Extraction Report

This document presents the complete extraction from:
1. `/home/yi/Downloads/PhantomTrace.docx` (Manuscript source text)
2. `/home/yi/Downloads/PhantomTrace_IEEE_Access_Revision_Notes.pdf` (Editorial notes)
3. Repository result files in `results/metrics/v3/`, `results/audits/`, `results/ablation/`, and `results/calibration/`

---

## (a) Bibliography: All 25 Cited References (Dataset, Method, Stated Limitation)

| Ref # | Citation (Author, Year, Title, Venue) | Dataset(s) Evaluated | Method / Classifier | Stated Limitation / Drawback Verifiable from Manuscript | Verification Status |
|:---:|:---|:---|:---|:---|:---:|
| **[1]** | Cantone M, Marrocco C, Bria A (2024) *Machine learning in network intrusion detection: a cross-dataset generalization study*. IEEE Access 12:144489–144508 | CIC-IDS2017, UNSW-NB15, CSE-CIC-IDS2018, NSL-KDD | RF, DT, MLP cross-dataset evaluation across standard NIDS benchmarks | Cross-dataset generalization collapses across heterogeneous schemas; models overfit to source network artifacts rather than transferable attack patterns. | Verified [1, 22] |
| **[2]** | Almuhanna R, Dardouri S (2025) *A deep learning/machine learning approach for anomaly based network intrusion detection*. Front Artif Intell 8:1625891 | CIC-IDS2017, NSL-KDD | Deep learning and unsupervised anomaly detection models | Evaluates predominantly in-distribution; threshold selection relies on test/validation balance without verifying threshold transferability across domains. | Verified [2, 12, 13] |
| **[3]** | Rainio O, Teuho J, Klén R (2024) *Evaluation metrics and statistical tests for machine learning*. Sci Rep 14:15724 | Multiple benchmark domains / synthetic benchmarks | Methodological and statistical analysis of ML metrics and hypothesis tests | Reviews pitfalls in single-metric reporting; demonstrates F1 is fragile and misleading under severe class imbalance; recommends MCC and paired testing. | Verified [3, 4, 24] |
| **[4]** | Semmelrock H, Ross-Hellauer T, Kopeinik S et al. (2024) *Reproducibility in machine learning-based research: overview, barriers and drivers*. arXiv:2406.14325 | ML literature meta-analysis | Survey of reproducibility practices in machine learning | Identifies lack of seed reporting, incomplete dataset split disclosures, and missing artifact availability as systemic barriers to independent replication. | Verified [3, 4, 24] |
| **[5]** | Xue P, Shen Y, Ma H, Hu M (2025) *An area-aware efficient internet-wide port scan approach for IoT*. Electronics 14(4):1267 | Internet-wide scan traces / IoT simulated traffic | Area-aware port scanning optimization and ML detection | Optimizes scanning from attacker perspective; intrusion evaluation lacks temporal holdout validation and realistic background noise. | Verified [5, 6] |
| **[6]** | Altidor JB, Talhi C (2024) *Enhancing port scan and DDoS attack detection using genetic and machine learning algorithms*. IEEE CloudNet / Cloud IoT 2024 | CIC-IDS2017 / custom lab traces | Genetic algorithm feature selection with RF and SVM | Conflates port scanning with volumetric DDoS into mixed attack classes; evaluates on random train-test partitions subject to flow-level leakage. | Verified [5, 6] |
| **[7]** | Okumura K, Kobayashi R (2025) *Penetration testing without port scanning using EPSS-based vulnerability lists*. CANDARW 2025, IEEE, pp 274–279 | EPSS vulnerability database / host profiles | Vulnerability prioritization avoiding traditional scanning | Restricts scope to host vulnerability exploitation rankings; does not analyze network flow-level traffic dynamics or detector transferability. | Verified [7, 17, 25] |
| **[8]** | Huang M, Lin Y, Li N et al. (2025) *CARD: robustness-preserving transfer learning for network intrusion detection*. IEEE TDSC 22(5):5134–5151 | CIC-IDS2017, UNSW-NB15, TON_IoT | Adversarial domain adaptation and transfer learning for NIDS | Solves domain shift via transfer learning but demonstrates that standard source models without adaptation suffer severe cross-domain performance collapse. | Verified [8, 9, 11] |
| **[9]** | Yao J, Tian L, Wei Z, Sun G (2025) *Overcoming emergency HTTP/3 DDoS attack detection: a domain adaptation solution with GNN*. Comput Netw 271:111611 | HTTP/3 simulated testbed traffic | Graph Neural Networks with domain adaptation | Evaluates volumetric DDoS rather than low-rate reconnaissance; evaluates only unidirectional adaptation. | Verified [8, 9, 11] |
| **[10]** | Anser O, François J, Chrisment I, Kondo D (2025) *TATA: benchmark NIDS test sets assessment and targeted augmentation*. ESORICS 2025, LNCS, pp 21–41 | CIC-IDS2017, UNSW-NB15 | Benchmark assessment framework exposing synthetic artifacts | Demonstrates that public NIDS benchmarks contain duplicate flows and synthetic artifacts that inflate F1 by up to 30% under random k-fold splits. | Verified [10, 16, 21] |
| **[11]** | Pawlicki M, Szelest S, Kozik R, Choraś M (2025) *SHAP insights into domain adaptation in netflow-based network intrusion detection*. ARES 2025, Springer | NF-UNSW-NB15-v2, NF-ToN-IoT-v2 | TreeSHAP attribution under domain adaptation | Investigates NetFlow feature shift under domain transfer but does not evaluate bidirectional transfer asymmetry or duplicate-frequency inflation. | Verified [8, 9, 11] |
| **[12]** | Wu Z, Liao X, He B et al. (2025) *Federated intrusion detection under non-IID traffic*. ProvSec 2025, pp 202–217 | UNSW-NB15, CIC-IDS2017 client partitions | Federated learning aggregation with anomaly detection | Focuses on client weight aggregation under non-IID distributions without testing cross-dataset deployment or threshold transferability. | Verified [2, 12, 13] |
| **[13]** | Alang K, Khanna A, Nalluri S (2026) *Enhancing network security: anomaly detection using generalised isolation forest and explainable AI*. ICGIS 2025, Springer | NSL-KDD, UNSW-NB15 | Generalized Isolation Forest with XAI (LIME/SHAP) | Assumes anomaly scores directly indicate intrusion; omits validation of decision-threshold shift and score polarity reversal under cross-domain transfer. | Verified [2, 12, 13] |
| **[14]** | Luay M, Layeghy S, Hosseininoorbin S et al. (2025) *Temporal analysis of NetFlow datasets for NIDS*. arXiv:2503.04404 | NetFlow versions of CIC-IDS2017, UNSW-NB15, TON_IoT | Temporal split evaluation vs random split evaluation | Demonstrates severe temporal concept drift causing large performance degradation under chronological evaluation relative to random splits. | Verified [14, 15, 20] |
| **[15]** | Khalid HYI, Aldabagh NBI (2024) *A survey on the latest intrusion detection datasets for SDN environments*. ETASR 14(2):13190–13200 | InSDN, CIC-DDoS2019, CIC-IDS2017 | Survey of SDN intrusion detection benchmarks | Identifies pervasive synthetic artifacts, artificial class balances, and lack of realistic stealth reconnaissance traffic in public benchmarks. | Verified [14, 15, 20] |
| **[16]** | Bilal MA, Islam IU, Idrees S et al. (2026) *Dataset-centric evaluation of federated intrusion detection models in IoT networks*. Sci Rep 2026 | IoT-23, Edge-IIoTset, BoT-IoT | Federated learning evaluation across IoT benchmarks | Shows severe cross-topology model degradation caused by benchmark-specific feature distributions and local network artifacts. | Verified [10, 16, 21] |
| **[17]** | Psychogyios K, Papadakis A, Bourou S et al. (2024) *Deep learning for intrusion detection systems in time series data*. Future Internet 16(3):73 | CIC-IDS2017, CSE-CIC-IDS2018 | LSTM, GRU, CNN sequential models | Evaluates time-series traffic but aggregates distinct attack classes without isolating low-rate, stealthy reconnaissance probes from volumetric attacks. | Verified [7, 17, 25] |
| **[18]** | Pawlicki M, Pawlicka A, Szelest S et al. (2025) *Class-based SHAP analysis for improved explainability insights in NIDS*. ICAI 2024, Springer | UNSW-NB15, CIC-IDS2017 | Class-conditioned SHAP analysis for multiclass NIDS | Restricted to in-distribution explainability; does not address how feature importance shifts when detectors are applied across foreign domains. | Verified [11, 18, 19] |
| **[19]** | Grzeczkowicz R, Neal C, Baghalizadeh-Moghadam N et al. (2025) *Classifying insider threat scenarios through explainable AI*. CRiSIS 2024, Springer | CERT insider threat dataset | Ensemble classifiers with SHAP / LIME explainers | Evaluates host audit logs and insider threat scenarios rather than network-layer reconnaissance traffic. | Verified [11, 18, 19] |
| **[20]** | Goldschmidt P, Chudá D (2025) *Network intrusion datasets: a survey, limitations, and recommendations*. Comput Secur 156:104510 | Survey of 25+ NIDS datasets (KDD99, CIC-IDS2017, UNSW-NB15, etc.) | Methodological critique and taxonomy | Comprehensively catalogues severe benchmark flaws: duplicate flows, synthetic label errors, unrealistic traffic rates, and inconsistent feature definitions. | Verified [14, 15, 20] |
| **[21]** | Belarbi O, Spyridopoulos T, Anthi E et al. (2025) *Gotham Dataset 2025: a reproducible large-scale IoT network dataset for intrusion detection*. arXiv:2502.03134 | Gotham IoT dataset | Reproducible testbed capture for IoT intrusion detection | Demonstrates legacy benchmarks (CIC-IDS2017, UNSW-NB15) contain heavy synthetic flow duplication and lack modern stealth reconnaissance tactics. | Verified [10, 16, 21] |
| **[22]** | Kostas K, Just M, Lones MA (2025) *Individual packet features are a risk to model generalisation in ML-based intrusion detection*. IEEE Netw Lett 7:66–70 | CIC-IDS2017, CTU-13 | Feature representation study (packet header vs flow aggregates) | Shows individual packet header features fail to generalize across networks, acting as shortcuts that artificially inflate in-distribution scores. | Verified [1, 22] |
| **[23]** | Aceto G, Giampaolo F, Guida C et al. (2024) *Synthetic and privacy-preserving traffic trace generation using generative AI for training NIDS*. JNCA 229:103926 | Mirai, CIC-IDS2017, enterprise traces | GANs and diffusion models for traffic synthesis | Evaluates synthetic trace generation fidelity but notes synthetic-to-real transfer frequently exhibits domain drop on real enterprise networks. | Verified [23] |
| **[24]** | Shaikhanova A, Kuznetsov O, Tokkuliyeva A et al. (2025) *Security audit of IoT device networks: a reproducible ML framework*. Sensors 25(24):7519 | IoT honeypot and testbed traces | Reproducible ML evaluation pipeline with statistical tests | Demonstrates that omitting statistical hypothesis testing and seed variance reporting leads to fragile benchmark conclusions. | Verified [3, 4, 24] |
| **[25]** | Mao J, Yang X, Hu B, Lu Y, Yin G (2025) *Intrusion detection system based on multi-level feature extraction and inductive network*. Electronics 14(1):189 | CIC-IDS2017, UNSW-NB15 | Inductive neural network with multi-level features | Reports high benchmark accuracy but uses random train/test splits without evaluating temporal holdout or bidirectional cross-dataset transfer. | Verified [7, 17, 25] |

---

## (b) All Result Tables Extracted from Files

### Table 1 · In-Distribution Temporal Holdout (`time_wise`, N = 2,021)
*Source: `results/metrics/v3/compiled_benchmark_tables.md` §1.1; confirmed by `results/metrics/v3/aggregate_summary.json`*

| Model | F1 (mean ± SD) | MCC (mean ± SD) | ROC-AUC (mean ± SD) | PR-AUC (mean ± SD) |
|:---|:---:|:---:|:---:|:---:|
| Random Forest (RF) | 0.9990 ± 0.0000 | 0.9980 ± 0.0000 | 0.9997 ± 0.0002 | 0.9997 ± 0.0002 |
| XGBoost (XGB) | 0.9990 ± 0.0000 | 0.9980 ± 0.0000 | 0.9999 ± 0.0000 | 0.9999 ± 0.0000 |
| Support Vector Machine (SVM) | 0.9976 ± 0.0002 | 0.9952 ± 0.0004 | 0.9995 ± 0.0000 | 0.9997 ± 0.0000 |
| Isolation Forest (IF) | 0.9961 ± 0.0011 | 0.9923 ± 0.0022 | 0.9971 ± 0.0003 | 0.9983 ± 0.0003 |
| Multi-Layer Perceptron (MLP) | 0.9990 ± 0.0000 | 0.9980 ± 0.0000 | 0.9985 ± 0.0000 | 0.9991 ± 0.0000 |

*Note: Prevalence baseline: 0.4904 (991 recon / 2,021 total). 54.8% of test rows (1,107/2,021) share exact feature vectors with training rows.*

### Table 2 · Temporal Holdout: Non-Overlapping Clean Subset (N = 914)
*Source: Manuscript text line 245; audit confirmed by `results/audits/domain_and_dedup_audit.json`*

| Model | F1 (clean subset, n=914) | MCC | ROC-AUC | 95% Bootstrap CI (ROC-AUC) |
|:---|:---:|:---:|:---:|:---:|
| Random Forest | 0.9375 ± 0.0000 | 0.9383 ± 0.0000 | 0.9995 ± 0.0002 | [0.9982, 1.0000] |
| XGBoost | 0.9375 ± 0.0000 | 0.9383 ± 0.0000 | 0.9998 ± 0.0001 | [0.9991, 1.0000] |
| SVM | 0.9091 ± 0.0000 | 0.9103 ± 0.0000 | 0.9992 ± 0.0001 | [0.9974, 1.0000] |
| Isolation Forest | 0.7286 ± 0.0432 | 0.7410 ± 0.0389 | 0.9942 ± 0.0012 | [0.9880, 0.9982] |
| MLP | 0.9375 ± 0.0000 | 0.9383 ± 0.0000 | 0.9981 ± 0.0001 | [0.9948, 1.0000] |

*Prevalence in clean subset: 0.0186 (17 recon / 914 total). Performance drops markedly once exact duplicates are removed.*

### Table 3 · Synthetic-to-Real Stress Test (`pcap_wise`, N = 168,930)
*Source: `results/metrics/v3/compiled_benchmark_tables.md` §1.2; `results/metrics/v3/aggregate_summary.json`*

| Model | F1 (mean ± SD) | MCC (mean ± SD) | ROC-AUC (mean ± SD) | PR-AUC (mean ± SD) |
|:---|:---:|:---:|:---:|:---:|
| Random Forest | 0.9924 ± 0.0001 | 0.8631 ± 0.0019 | 0.9942 ± 0.0006 | 0.9994 ± 0.0001 |
| XGBoost | 0.9912 ± 0.0000 | 0.8436 ± 0.0000 | 0.8699 ± 0.0000 | 0.9841 ± 0.0000 |
| SVM | 0.0000 ± 0.0000 | −0.0242 ± 0.0000 | 0.4994 ± 0.0000 | 0.9411 ± 0.0000 |
| Isolation Forest | 0.5960 ± 0.5434 | 0.5332 ± 0.4871 | **0.9970 ± 0.0006** | 0.9998 ± 0.0001 |
| MLP | 0.0016 ± 0.0000 | −0.0248 ± 0.0089 | 0.6397 ± 0.1444 | 0.9497 ± 0.0152 |

*Prevalence baseline: 0.9408 (158,930 recon / 168,930 total). Train = 86 synthetic rows.*
*IF per-seed F1: 0.0016 (seed 42), 0.9892 (seed 7), 0.9950 (seed 13), 0.0000 (seed 99), 0.9950 (seed 2024). Bimodality reflects polarity inversion across seeds.*

### Table 4 · Primary Cross-Dataset Transfer: UNSW-NB15 → CIC-IDS-2017 (N = 168,930)
*Source: `results/metrics/v3/compiled_benchmark_tables.md` §1.4; `results/metrics/v3/aggregate_summary.json`*

| Model | F1 (mean ± SD) | MCC (mean ± SD) | 95% Bootstrap CI (MCC) | ROC-AUC (mean ± SD) | PR-AUC (mean ± SD) |
|:---|:---:|:---:|:---:|:---:|:---:|
| MLP | **0.9947 ± 0.0001** | **0.9181 ± 0.0021** | [0.9135, 0.9239] | **0.9845 ± 0.0039** | **0.9966 ± 0.0022** |
| Random Forest | 0.5160 ± 0.3732 | 0.1719 ± 0.2514 | [0.0891, 0.2547] | 0.8341 ± 0.0163 | 0.9770 ± 0.0030 |
| XGBoost | 0.2270 ± 0.0000 | −0.0719 ± 0.0000 | [−0.1121, −0.0331] | 0.7404 ± 0.0000 | 0.9728 ± 0.0000 |
| Isolation Forest | 0.0671 ± 0.1060 | −0.2025 ± 0.1440 | [−0.2827, −0.1711] | 0.8376 ± 0.0129 | 0.9012 ± 0.0124 |
| SVM | 0.0000 ± 0.0000 | −0.0291 ± 0.0000 | [−0.0480, −0.0039] | **0.9917 ± 0.0000** | **0.9987 ± 0.0000** |

*Prevalence: 0.9408. Notice SVM achieves ROC-AUC = 0.9917 with F1 = 0.0000.*

### Table 5 · Reverse Cross-Dataset Transfer: CIC-IDS-2017 → UNSW-NB15 (N = 5,277)
*Source: `results/metrics/v3/compiled_benchmark_tables.md` §1.5; `results/metrics/v3/aggregate_summary.json`*

| Model | F1 (mean ± SD) | MCC (mean ± SD) | 95% Bootstrap CI (MCC) | ROC-AUC (mean ± SD) | PR-AUC (mean ± SD) |
|:---|:---:|:---:|:---:|:---:|:---:|
| MLP | 0.0011 ± 0.0000 | 0.0195 ± 0.0000 | [0.0000, 0.0373] | **0.8330 ± 0.0003** | 0.6947 ± 0.0030 |
| Isolation Forest | 0.0005 ± 0.0006 | 0.0000 ± 0.0066 | [0.0000, 0.0373] | **0.8095 ± 0.0228** | 0.5989 ± 0.0378 |
| SVM | 0.0011 ± 0.0000 | 0.0195 ± 0.0000 | [0.0000, 0.0373] | 0.4447 ± 0.0006 | 0.3879 ± 0.0002 |
| XGBoost | 0.0011 ± 0.0000 | 0.0195 ± 0.0000 | [0.0000, 0.0373] | 0.6120 ± 0.0000 | 0.4749 ± 0.0000 |
| Random Forest | 0.0011 ± 0.0000 | 0.0195 ± 0.0000 | [0.0000, 0.0373] | 0.4085 ± 0.0878 | 0.3228 ± 0.0754 |

*Prevalence: 0.3333 (1,759 recon / 5,277 total). Complete collapse across all models in this direction.*

### Table 6 · Duplicate-Cap Analysis for All 5 Models in Both Transfer Directions
*Source: `results/audits/domain_and_dedup_audit.json` §deduplication_sensitivity*

**Direction 1: UNSW → CIC (Test N = 168,930 down to 10,711)**

| Cap Level | Test N | Recon N | RF F1 | XGB F1 | SVM F1 | IF F1 | MLP F1 |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Unique (Cap ≤ 1)** | 10,711 | 1,921 | 0.028 | 0.045 | 0.001 | 0.255 | 0.360 |
| **Cap ≤ 2** | 11,383 | 2,276 | 0.049 | 0.064 | 0.001 | 0.246 | 0.498 |
| **Cap ≤ 5** | 12,715 | 3,180 | 0.095 | 0.107 | 0.001 | 0.225 | 0.677 |
| **Cap ≤ 10** | 14,230 | 4,498 | 0.141 | 0.155 | 0.000 | 0.200 | 0.787 |
| **Uncapped (Full)** | 168,930 | 158,930 | 0.191 | 0.227 | 0.000 | 0.015 | **0.995** |

**Direction 2: CIC → UNSW (Test N = 5,277 down to 4,523)**

| Cap Level | Test N | Recon N | RF F1 | XGB F1 | SVM F1 | IF F1 | MLP F1 |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Unique (Cap ≤ 1)** | 4,523 | 1,075 | 0.0019 | 0.0019 | 0.0019 | 0.0021 | 0.0019 |
| **Cap ≤ 2** | 4,615 | 1,114 | 0.0018 | 0.0018 | 0.0018 | 0.0041 | 0.0018 |
| **Cap ≤ 5** | 4,686 | 1,168 | 0.0017 | 0.0017 | 0.0017 | 0.0040 | 0.0017 |
| **Cap ≤ 10** | 4,752 | 1,234 | 0.0016 | 0.0016 | 0.0016 | 0.0039 | 0.0016 |
| **Uncapped (Full)** | 5,277 | 1,759 | 0.0011 | 0.0011 | 0.0011 | 0.0034 | 0.0011 |

### Table 7 · Unit-Normalization & Feature-Ablation Study (`flow_interval_mean`)
*Source: `results/ablation/interval_ablation_results.json` (5 seeds, mean ± SD)*

| Direction | Feature Condition | RF F1 | XGB F1 | SVM F1 | IF F1 | MLP F1 | RF ROC-AUC | MLP ROC-AUC |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **UNSW → CIC** | 11-feat baseline | 0.8063 | 0.2269 | 0.0000 | 0.1538 | 0.9948 | 0.8464 | 0.9846 |
| | 10-feat (no `flow_interval_mean`) | **0.9818** | **0.9812** | 0.0000 | 0.0253 | **0.9915** | 0.9393 | 0.9628 |
| | `flow_interval_mean` only | 0.4444 | 0.3074 | 0.4307 | 0.1760 | 0.3876 | 0.6924 | 0.7490 |
| | 11-feat (unit-normalized / z-scored) | 0.8063 | 0.2269 | 0.0000 | 0.1538 | 0.9948 | 0.8464 | 0.9846 |
| **CIC → UNSW** | 11-feat baseline | 0.0011 | 0.0000 | 0.0011 | 0.0241 | 0.0011 | 0.4971 | 0.8330 |
| | 10-feat (no `flow_interval_mean`) | 0.0011 | 0.0000 | 0.0000 | 0.0241 | 0.0011 | 0.2854 | 0.8332 |
| | `flow_interval_mean` only | **0.5201** | **0.4860** | **0.5020** | **0.3006** | **0.5007** | 0.6256 | 0.4282 |
| | 11-feat (unit-normalized / z-scored) | 0.0011 | 0.0000 | 0.0011 | 0.0241 | 0.0011 | 0.4732 | 0.8330 |

*Key finding: Removing `flow_interval_mean` allows RF and XGBoost to recover to F1 = 0.981 in UNSW→CIC! However, in the reverse direction (CIC→UNSW), 10 features still yields F1 = 0.0011 because source-trained decision boundaries do not separate target distributions. When tested ON `flow_interval_mean` ONLY, models achieve F1 ≈ 0.50 in CIC→UNSW!*

### Table 8 · Post-Hoc Threshold Calibration Experiment (Platt Scaling & Isotonic Regression)
*Source: `results/calibration/calibration_results.json` (5 seeds)*

| Evaluation Case | Model | Uncalibrated F1 | Platt (0.5 thresh) | Isotonic (0.5 thresh) | Source-Optimal Val Thresh | ROC-AUC |
|:---|:---|:---:|:---:|:---:|:---:|:---:|
| **UNSW → CIC** | SVM | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | 0.9917 ± 0.0000 |
| | RF | 0.8063 ± 0.2926 | 0.3748 ± 0.3444 | 0.5489 ± 0.3957 | 0.1363 ± 0.1009 | 0.8464 ± 0.0206 |
| | MLP | 0.9948 ± 0.0001 | 0.9946 ± 0.0001 | 0.9946 ± 0.0001 | 0.9946 ± 0.0001 | 0.9846 ± 0.0022 |
| **CIC → UNSW** | SVM | 0.0011 ± 0.0000 | 0.0011 ± 0.0000 | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | 0.7216 ± 0.0007 |
| | MLP | 0.0011 ± 0.0000 | 0.0011 ± 0.0000 | 0.0011 ± 0.0000 | 0.0000 ± 0.0000 | 0.8330 ± 0.0002 |
| **Synthetic-to-Real** | MLP | 0.0016 ± 0.0000 | 0.0016 ± 0.0000 | 0.0016 ± 0.0000 | 0.0016 ± 0.0000 | 0.6154 ± 0.1444 |
| | RF | 0.9955 ± 0.0026 | 0.9920 ± 0.0000 | 0.9934 ± 0.0022 | 0.0000 ± 0.0000 | 0.9942 ± 0.0006 |

*Key finding: Source-domain calibration (Platt/isotonic) fits the probability curve to the SOURCE validation set. Under domain shift, the target domain feature distribution shifts the output logits into an entirely uncalibrated range; therefore, source calibration DOES NOT restore F1 to high-ROC cases (e.g. SVM ROC-AUC = 0.9917 remains F1 = 0.0000).*

### Table 9 · Domain Separability Classifier
*Source: `results/audits/domain_and_dedup_audit.json` §domain_origin_classifier*

A 5-fold CV Random Forest trained to distinguish CIC from UNSW flows achieves ROC-AUC = **0.999993 ± 0.000010**.
Feature importances:
1. `flow_interval_mean`: 0.3044
2. `flow_size_mean`: 0.2762
3. `flow_bytes`: 0.2217
4. `flow_packet_count`: 0.1160
5. `flow_duration`: 0.0818

---

## (c) Experiment Completeness Assessment

| Revision Note Experiment | Status | Evidence / Location |
|:---|:---:|:---|
| **Single final pipeline rerun** | ✅ COMPLETE | `results/metrics/v3/` contains 255 per-seed JSON files for all models × conditions × schemas × 5 seeds. Audits PASS. |
| **Unit-normalization & removal ablation** | ✅ COMPLETE | `results/ablation/interval_ablation_results.json` generated for all 5 models × 2 directions × 4 conditions × 5 seeds. |
| **Duplicate analysis for all 5 models in both directions** | ✅ COMPLETE | `results/audits/domain_and_dedup_audit.json` contains full dose-response curves (caps ≤1, ≤2, ≤5, ≤10, full) for RF, XGB, SVM, IF, MLP in both UNSW→CIC and CIC→UNSW. |
| **Third dataset (NF-ToN-IoT-v2)** | ❌ MISSING | Script exists (`experiments/evaluate_third_dataset.py`), but raw PCAP/NetFlow dataset was not downloaded and benchmark directory is empty. To be framed as planned future work. |
| **Calibration (Platt / isotonic)** | ✅ COMPLETE | `results/calibration/calibration_results.json` generated for 5 seeds across all anomaly/collapse conditions. |
| **Statistics clarification (5 seeds = optimization variability)** | ✅ COMPLETE | Formulated in code, manuscript, and audit notes. |
| **Pairwise McNemar's with Holm correction & Bootstrap CIs** | ✅ COMPLETE | Documented in `results/metrics/v3/redesigned_statistical_tests.json`. |
"""

with open("phantomtrace_complete_extraction_report.md", "w") as f:
    f.write(report)

print("Saved phantomtrace_complete_extraction_report.md")
