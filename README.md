# VolMax Great Britain BESS Fleet Audit (June 2026)
### Level 1–4 Physical & Data-Integrity Audit under the P10 Verification Protocol

This repository contains the code, registry data, and data integrity checks to audit the operational dispatch of all grid-scale Battery Energy Storage Systems (BESS) in Great Britain for the month of **June 2026**.

The audit covers **136 unique BESS units** registered with the Elexon Balancing Mechanism.

---

## 1. Audit Methodology & P10 Battery Annex

This audit is executed in strict adherence to **P10 v1.0** and the **P10 Battery Annex (Part 1: Grid-Dispatch)**. It performs the following checks:
*   **L1 Data Integrity**: Verifies completeness of active power telemetry and sign conventions (positive for discharge/export, negative for charge/import).
*   **L2 Physical Consistency**: Computes the AC-to-AC round-trip efficiency ($\eta_{\text{RTE, AC}}$) at the grid connection boundary over a 30-day window. Flags physical violations if $\eta_{\text{RTE, AC}} > 0.92$ (thermodynamic impossibility, under-reported charging or auxiliary load exclusion) or $\eta_{\text{RTE, AC}} < 0.60$ (abnormal leakage/losses).
*   **L3 Registry & COD Screening**: Excludes inactive or pre-COD (commissioning) units with total monthly throughput $<1.0\text{ MWh}$ from active fleet statistics.
*   **L4 Mathematical Reproducibility**: Data is frozen in a local JSON archive. The pipeline verifies that the local file's SHA-256 matches the cryptographic signature in `data_manifest.json` before execution.

---

## 2. Getting Started

### Prerequisites
*   Python 3.x
*   `requests` library (only required if pulling new raw data)

To install dependencies:
```bash
pip install requests
```

### Reproducing the Audit (P10-L4)
To verify the audit results using the pinned, frozen raw data archive:
```bash
python3 reproduce.py
```
This script will:
1. Validate the SHA-256 hash of the local raw data against the manifest.
2. Ingest the dataset, apply active/inactive screening, verify telemetry signs, and compute RTEs.
3. Save the detailed per-unit results to `audit_metrics.json`.
4. Output a summary report of passed/failed units.

### Fetching New Data (Optional)
To pull fresh raw B1610 telemetry from the Elexon Insights Solution API:
```bash
python3 pull_elexon.py --start 2026-06-01 --end 2026-07-01 --output data/raw_b1610_202606.json
```
*Note: Because Elexon metered volumes are subject to subsequent settlement runs (II, SF, R1, R2, R3, RF, DF) over a multi-year timeline, fresh API pulls may return revised values that mismatch the original manifest hash.*

---

## 3. Licensing Layering

This repository uses a layered licensing model:
*   **Code & Scripts**: Licensed under the [MIT License](LICENSES.md#1-code--scripts-mit-license).
*   **Raw Telemetry Data Archive**: Sourced from the Elexon Insights Solution and distributed under the [BSC Public Data Licence](LICENSES.md#2-raw-telemetry-data-bsc-public-data-licence) with the mandatory attribution:
    > *"Contains BSC information that is available from Elexon at no charge and which is licensed under the Elexon Public Data Licence."*
*   **Derived Audit Metrics**: Distributed under the [Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSES.md#3-derived-metrics--reports-cc-by-4-0).
