# Data Governance Policy & Dataset Registry

## 1. Overview
This policy establishes baseline governance standards for datasets ingested, cached, or trained within the **Błyskawica / Adaptive Neural Network** ecosystem.

## 2. Core Governance Principles
- **Provenance Verification**: All datasets ingested via CLI or dynamic download (e.g. KaggleHub) must have a verified origin URL, author, and timestamp.
- **License Compliance**: Datasets must possess a permissive open license (e.g. MIT, CC-BY, Apache 2.0). Proprietary or restricted datasets must be isolated from public model weights.
- **PII & Privacy Policy**: No personally identifiable information (PII) or unanonymized biometric data may be stored in raw text or committed to checkpoints.
- **Retention & Deletion**: Datasets stored in local cache (`~/.cache/adaptiveneuralnetwork/` or `data/`) must support purge on demand via `python train.py --purge-cache`.

## 3. Dataset Registry & Risk Matrix

| Dataset Identifier | Primary Use Case | Provenance | License | PII Risk Level | Verification Gate |
|-------------------|------------------|------------|---------|----------------|-------------------|
| `mnist` | Image Classification Benchmark | PyTorch torchvision / Yann LeCun | CC BY-SA 3.0 | Low (Synthetic/Digits) | Automated |
| `cifar10` | Object Recognition Benchmark | PyTorch torchvision / Alex Krizhevsky | MIT | Low (Natural Images) | Automated |
| `annomi` | Conversational Analysis | Kaggle / Research | Public Domain | Low (Anonymized Dialogues) | Manual Review |
| `mental_health` | Text Sentiment / Categorization | Open Benchmark | CC0: Public Domain | Medium (Text Samples) | Anonymization Gate |
| `vr_driving` | Telemetry & Spatial Control | Internal Simulation | Proprietary / Internal | Low (Synthetic Telemetry) | Automated |
| `autvi` / `digakust` | Audio / Acoustic Signals | Acoustic Research Repository | CC-BY 4.0 | Low (Sensor Data) | Schema Validation |

## 4. Ingestion Schema Validation
All custom dataset loaders must implement a Pydantic schema validator ensuring required columns and tensor dimensions match prior to batch collation.
