# VolMax Great Britain BESS Fleet Data-Integrity Screening (June 2026)
### Level 1–2 Data-Integrity Screening under the P10 Verification Protocol (L1–L2 Scope)

This repository contains the code, registry data, and data screening checks to perform a fleet-wide Level 1–2 data-integrity and physical consistency screening of grid-scale Battery Energy Storage Systems (BESS) in Great Britain for the month of **June 2026**.

This fleet-wide screening does not constitute a full Level 3–5 P10 audit for all units. Full P10 audits (requiring a pre-registered prep plan, localized decision ledger, and final verdict) are reserved for selected assets (such as the Pillswood BESS audit in the `audits/` directory) which pass through the complete audit gate ledger.

The screening covers **137 unique BESS units** registered with the Elexon Balancing Mechanism.

---

## 1. Screening Methodology & P10 Battery Annex

This screening is executed in adherence to the Level 1 and Level 2 guidelines of the **P10 v1.1** protocol and the **P10 Battery Annex (Part 1: Grid-Dispatch)**. It performs the following checks:

*   **L1 Data Integrity**: Verifies completeness of active power telemetry and sign conventions (positive for discharge/export, negative for charge/import). Identifies units with single-direction telemetry (always charging or always discharging).
*   **L2 Physical Consistency**: Computes the AC-to-AC round-trip efficiency ($\eta_{\text{RTE, AC}}$) at the grid connection boundary over the 30-day window. 
    *   **Thermodynamic Failure Gate**: Flags physical violations if $\eta_{\text{RTE, AC}} > 1.0$, which is a strict thermodynamic impossibility (more energy exported than imported, indicating serious telemetry or metering errors).
    *   **Descriptive Flags**: The standard operating range of 0.60–0.92 is used as a descriptive boundary. Values outside this range (but $\le 1.0$) or below 0.60 are flagged as anomalies. *Crucially, monthly per-unit AC-AC RTE calculations without State-of-Charge (SoC) closing are dominated by boundary condition edge effects (e.g., a battery starting the month full and ending empty can show an apparent RTE > 1.0, and vice versa). This is a known boundary-artifact caveat and does not necessarily imply physical equipment failure.*
*   **L3 Registry & COD Screening**: Excludes inactive or pre-commissioning (pre-COD) units with total monthly throughput $< 1.0\text{ MWh}$ from active fleet statistics.
*   **L4 Mathematical Reproducibility**: Telemetry data is frozen in a local JSON archive. The pipeline verifies that the local file's SHA-256 matches the cryptographic signature in `data_manifest.json` before execution.

### Registry Source & Data Provenance
The fleet registry (`bess_registry.json`) is compiled from Elexon Balancing Mechanism registration lists filtered by technology class (BESS) and Lead Party Name, capturing a snapshot of the active GB BESS fleet as of June 2026. This method ensures that BESS units with netipičnim (non-standard) names are not omitted, maintaining comprehensive coverage.

---

## 2. Getting Started

### Prerequisites
*   Python 3.x
*   `requests` library (only required if pulling new raw data)

To install dependencies:
```bash
pip install requests
```

### Reproducing the Screening (P10-L4)
To verify the screening results using the pinned, frozen raw data archive:
```bash
python3 reproduce.py
```
This script will:
1. Validate the SHA-256 hash of the local raw data against the manifest.
2. Ingest the dataset, apply active/inactive screening, verify telemetry signs, and compute RTEs.
3. Save the detailed per-unit results to `audit_metrics.json`.
4. Output a summary report of passed, failed, and flagged units.

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
*   **Derived Screening Metrics**: Distributed under the [Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSES.md#3-derived-metrics--reports-cc-by-4-0).

