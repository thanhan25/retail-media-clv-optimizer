
# Retail Media CLV Optimizer 📊

[![Continuous Integration Quality Gate](https://github.com/thanhan25/retail-media-clv-optimizer/actions/workflows/ci.yml/badge.svg)](https://github.com/thanhan25/retail-media-clv-optimizer/actions)
![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue.svg)
![Test Coverage](https://img.shields.io/badge/coverage-98.67%25-green.svg)

A production-grade predictive business intelligence engine designed to transform raw transactional data lake records into decision-ready Customer Lifetime Value (CLV) forecasts. This architecture isolates statistical frequency calculations, models customer retention variances, and implements defensive data validation layers to assist Sales Operations, Logistics, and Finance teams.

## 🏗️ Architecture Design & Quality Standards

- **PEP 517 Build Standards:** Engineered using modern, robust package distributions (`pyproject.toml` with `setuptools` find maps) to ensure predictable, environment-isolated execution.
- **Context-Managed Storage Layers:** Implements zero-dangling connection context loops to handle active data storage sessions with automated transaction rollbacks under driver exception conditions.
- **Decoupled Domain Exceptions:** Eradicates ambiguous native string error matching by utilizing specialized, custom exception tracking layers (`DataLakeExtractionError`, `ModelFittingInversionError`).
- **Strict Quality Gates:** Covered by a comprehensive unit testing framework enforcing a strict minimum **90% test coverage gate** check.
- **Continuous Integration (CI):** Backed by an active GitHub Actions orchestration matrix validating code style rules (`black`, `isort`) and executing regression matrices automatically across multiple Python target versions on every push.

## 📦 Core Package Map

```text
retail-media-clv-optimizer/
│
├── .github/workflows/
│   └── ci.yml               # Automated multi-version execution engine
│
├── src/clv_optimizer/
│   ├── __init__.py          # Package declaration hook
│   ├── config.py            # Centralized environment configurations vault
│   ├── database.py          # Context-managed connection session provider
│   ├── exceptions.py        # Independent domain error tracking hierarchies
│   └── pipeline.py          # Primary BG/NBD-modeled calculation matrix
│
├── tests/
│   └── test_pipeline.py     # Persistent sandboxed data lake integration test array
│
└── pyproject.toml           # Unified metadata manifest and distribution configuration
```


## 🚀 Installation & Environment Setup

Ensure you have Python 3.11+ active, then clone the repository and install it in editable development mode:

```bash
# Clone the repository asset line
git clone [https://github.com/thanhan25/retail-media-clv-optimizer.git](https://github.com/thanhan25/retail-media-clv-optimizer.git)
cd retail-media-clv-optimizer

# Ingest package configurations with local development testing metrics
python -m pip install -e .[dev]
```

## 🏃‍♂️ Running the Quality Assurance Suite

Execute the unified testing matrices locally and generate comprehensive code health coverage analytics tables using the module execution runner:

```bash
python -m pytest
```

```

```
