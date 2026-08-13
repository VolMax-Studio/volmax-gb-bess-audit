# VolMax Great Britain BESS Fleet Screening & Pillswood Capacity Audit
**Protocol Version:** `P10 v1.1` | **Audit ID:** `VM-2026-0002`

This repository contains the code, registry data, and data integrity checks to perform a fleet-wide Level 1–2 screening of grid-scale Battery Energy Storage Systems (BESS) in Great Britain for June 2026, alongside a full Level 3–5 P10 capacity verification audit for the **Pillswood BESS asset (`UK-HARMONY-001`)**.

The screening covers **137 unique BESS units** registered with the Elexon Balancing Mechanism, with full P10 audit artifacts (pre-registration rules, decision ledgers, and deterministic metrics) housed in `audits/UK-HARMONY-001/`.

---

## 1. Methodology & P10 Protocol

This audit package adheres strictly to the guidelines of the **P10 v1.1** protocol and the **P10 Battery Annex (Part 1: Grid-Dispatch)**:

*   **L1 Data Integrity**: Verifies completeness of active power telemetry and sign conventions (positive for discharge/export, negative for charge/import) against pinned SHA-256 hashes in `data_manifest.json`.
*   **L2 Physical Consistency**: Computes AC-to-AC round-trip efficiency ($\eta_{\text{RTE, AC}}$) at the grid connection boundary. Flags physical violations ($\eta_{\text{RTE, AC}} > 1.0$) and evaluates operating bounds.
*   **L3 Registry & COD Screening**: Filters pre-commissioning (pre-COD) units with monthly throughput $< 1.0\text{ MWh}$ from active fleet statistics.
*   **L4 Mathematical Reproducibility**: Pure Python Standard Library single entry point (`reproduce.py`) deterministically regenerates primary asset findings (`metrics_12m.json`) and secondary scoped asset metrics (`metrics.json`) from frozen raw telemetry with zero third-party package dependencies.

### Registry Source & Data Provenance
The fleet registry (`bess_registry.json`) is compiled from Elexon Balancing Mechanism registration lists filtered by technology class (BESS) and Lead Party Name, capturing a snapshot of the active GB BESS fleet as of June 2026. This method ensures that BESS units with non-standard names are not omitted.

---

## 2. Getting Started

### Prerequisites
*   **Python 3.8+** (Standard Library only — no external packages required for audit verification).

### Reproducing the Audit (P10-L4)
To deterministically regenerate the primary and secondary audit metrics from the pinned, frozen telemetry archive:
```bash
python3 reproduce.py
```
This single entry point script will:
1. Validate the SHA-256 hash of `raw_pillswood_12m.json` against `data_manifest.json` (halts with exit code 1 on mismatch).
2. Process 34,940 telemetry records across 12 calendar months (July 2025 – June 2026).
3. Deterministically regenerate `metrics_12m.json` (primary 12-month asset findings) and `metrics.json` (secondary June 2026 scoped asset metrics).
4. Verify execution completeness with 0 numeric diff against canonical project hashes.

External verification of the audit package is verified via:
```bash
cd audits/UK-HARMONY-001
sha256sum -c SHA256SUMS
```

### Fetching New Data (Optional)
To pull fresh raw B1610 telemetry from the Elexon Insights API (requires `requests` library):
```bash
python3 pull_elexon.py --start 2026-06-01 --end 2026-07-01 --output data/raw_b1610_202606.json
```
*Note: Because Elexon metered volumes are subject to subsequent settlement runs (II, SF, R1, R2, R3, RF, DF) over a multi-year timeline, fresh API pulls may return revised values that mismatch the original manifest hash.*

---

## 3. Licensing Layering

This repository uses a 3-part layered licensing model (documented in `audits/UK-HARMONY-001/NOTICE` and `LICENSES.md`):
*   **Code & Verification Scripts (`reproduce.py`)**: Licensed under the [MIT License](LICENSES.md#1-code--scripts-mit-license).
*   **Raw Telemetry Data Archive (`raw_pillswood_12m.json`)**: Sourced from Elexon BMRS and distributed under the [BSC Public Data Licence](LICENSES.md#2-raw-telemetry-data-bsc-public-data-licence) with attribution:
    > *"Contains BMRS data © Elexon Limited copyright and database right 2025–2026"*
*   **Derived Metrics & Audit Reports (`report.md`)**: Distributed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSES.md#3-derived-metrics--reports-cc-by-4-0).
