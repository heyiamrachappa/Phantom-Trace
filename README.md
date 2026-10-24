# PhantomTrace

A reproducible cross-dataset and temporal evaluation framework for machine learning-based network reconnaissance detection.

---

## Table of Contents
- [Overview](#overview)
- [System Requirements](#system-requirements)
- [Installation](#installation)
  - [Automated Setup](#option-a-automated-setup)
  - [Manual Setup](#option-b-manual-setup)
  - [Live Packet Capture Privileges (Optional)](#packet-capture-permissions-optional)
- [How to Run](#how-to-run)
  - [1. Web Forensic Dashboard (Streamlit GUI)](#1-interactive-forensics-dashboard-streamlit)
  - [2. End-to-End Validation Test](#2-end-to-end-validation-pipeline)
  - [3. Real-Time Streaming Intrusion Detector CLI](#3-real-time-streaming-intrusion-detector-cli)
  - [4. Dataset Extraction Pipeline](#4-feature-extraction--dataset-pipeline)
  - [5. Model Training & Evaluation](#5-model-suite-training--evaluation)
- [Project Architecture](#project-architecture)
- [Configuration](#configuration)

---

## Overview

**PhantomTrace** is an end-to-end network security framework designed to detect stealth reconnaissance (such as slow port scans, half-open SYN scans, horizontal/vertical sweeps) using flow-level statistical metrics, entropy analysis, and machine learning models (Random Forest, XGBoost, SVM, Isolation Forest).

---

## System Requirements

- **Operating System**: Linux (Ubuntu 20.04+, 22.04+, 24.04+, 26.04) or macOS / WSL2
- **Python**: Python 3.10, 3.11, or 3.12 (Python 3.11/3.12 recommended for pre-built ML wheels)
- **System Utilities**: `libpcap-dev`, `tcpdump`, `python3-venv`, `python3-pip`

---

## Installation

### Option A: Automated Setup

The repository includes a provisioning script `setup.sh`:

```bash
# 1. Install system prerequisites (Debian/Ubuntu)
sudo apt update
sudo apt install -y python3-venv python3-pip libpcap-dev tcpdump libcap2-bin \
    python3-pandas python3-numpy python3-sklearn python3-scipy python3-matplotlib python3-xgboost python3-joblib

# 2. Run automated setup
chmod +x setup.sh
./setup.sh

# 3. Activate the virtual environment
source venv/bin/activate
```

### Option B: Manual Setup

If you prefer to configure manually:

```bash
# 1. Install system packages
sudo apt update
sudo apt install -y python3-venv python3-pip libpcap-dev tcpdump

# 2. Create and activate a Python virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# (Optional) Install research experiment dependencies (SHAP, PyArrow, etc.)
pip install shap pyarrow imbalanced-learn
```

### Packet Capture Permissions (Optional)

If you plan to run **live** packet capture on physical/virtual network interfaces without running as `root` or `sudo`:

```bash
sudo setcap cap_net_raw,cap_net_admin+eip venv/bin/python3
```

*(Note: If you run detection using offline `.pcap` simulation files, no root or `setcap` privileges are required).*

---

## How to Run

Make sure your virtual environment is active before running any commands:
```bash
source venv/bin/activate
```

### 1. Interactive Forensics Dashboard (Streamlit)

Launch the web workstation to inspect PCAPs, view flow telemetry, run live or simulated packet detection, and generate reports:

```bash
streamlit run app.py
```

By default, the dashboard starts on port `8501`. Access it at:
```
http://localhost:8501
```

To bind to a specific host and port (e.g., remote server or cloud):
```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

### 2. End-to-End Validation Pipeline

To verify all system components (synthetic PCAP creation, feature extraction, model training, and streaming alert verification):

```bash
python3 validate.py
```

Expected output:
- Generates `pcaps/synthetic_scan.pcap`
- Extracts flow features into `dataset/train_features.csv` and `test_features.csv`
- Trains model suite and tests metrics
- Emulates streaming packet detection and outputs alerts into `logs/alerts.log`

### 3. Real-Time Streaming Intrusion Detector CLI

The standalone detection engine can run in two modes:

#### PCAP Simulation Mode (Safe, no root required):
Emulates live packet flow from a captured file:
```bash
python3 realtime_detector.py -s pcaps/synthetic_scan.pcap -m random_forest
```

Available models (`-m`): `random_forest`, `xgboost`, `svm`, `isolation_forest`.

#### Live Network Sniffing Mode:
Captures packets directly from a network interface:
```bash
python3 realtime_detector.py -i eth0 -m random_forest -d 60
```
- `-i`: Interface (e.g. `eth0`, `wlan0`, or `any`)
- `-d`: Duration in seconds (`0` for continuous)

Alerts are written to `logs/alerts.log`.

### 4. Feature Extraction & Dataset Pipeline

To extract statistical flow features and perform heuristic labeling from custom PCAP files:

```bash
python3 pipeline.py pcaps/synthetic_scan.pcap -s 192.168.1.187 -t 0.2
```
- First positional argument: One or more PCAP file paths
- `-s` / `--scanners`: Comma-separated list of known attacker IPs for supervised labeling
- `-t` / `--test-size`: Test split ratio (default: 0.2)

Generated datasets are stored in `dataset/` and scalers/feature lists in `models/`.

### 5. Model Suite Training & Evaluation

To train and evaluate all baseline ML models against the current preprocessed datasets:

```bash
python3 models/engine.py --train
```

Outputs:
- Serialized models in `models/*.joblib`
- ROC curves, confusion matrices, and feature importance charts in `results/`

---

## Project Architecture

```
Phantom-Trace/
├── app.py                      # Dashboard application entry point
├── pipeline.py                 # PCAP to dataset extraction pipeline
├── realtime_detector.py        # Real-time streaming IDS orchestrator
├── validate.py                 # Full integration test script
├── setup.sh                    # Automated provisioning & setup script
├── requirements.txt            # Core Python package dependencies
├── configs/
│   └── config.json             # Global hyperparameters & thresholds
├── dashboard/                  # Streamlit forensic workstation UI
├── capture/                    # Scapy packet sniffer & packet record dataclass
├── flows/                      # Sliding window bidirectional flow tracker
├── features/                   # Flow and host entropy feature extraction
├── detection/                  # ML inference engine for online classification
├── models/                     # Model training engine and serialized weights
├── alerts/                     # Explainable alert generator and log writer
├── threat_analysis/            # Attribution, behavioral profiling & threat intel
├── reporting/                  # Forensic PDF/Markdown summary generator
└── pcaps/                      # Captured network PCAP samples
```

---

## Configuration

System parameters, window sizes, entropy thresholds, and ML hyperparameters can be configured in [configs/config.json](file:///home/spidey/PROJECTS/Phantom-Trace/configs/config.json).
