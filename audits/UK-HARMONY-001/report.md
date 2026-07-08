# P10 Verification Report: Pillswood BESS Grid-Dispatch Audit
### Report ID: `VM-2026-0002` | Protocol Version: `P10 v1.0`
**Claim ID:** `UK-HARMONY-001` (Pillswood Battery Storage)

```yaml
Measurement Anchor:
  Dataset: BMRS B1610
  Resolution: 30 minutes
  Observable:
    - Net import/export energy volume (MWh)
    - Settlement-period average active power (MW)
  Not Observable:
    - State of Charge (SoC)
    - Cell-level voltage / temperature
    - Instantaneous active / reactive power spikes
    - Sub-second ancillary service response (e.g. Dynamic Containment)
```

This report presents the P10 verification sequence and final verdicts for the active power and energy storage capacity claims of Harmony Energy's Pillswood BESS.

---

## 1. Executive Summary

*   **Claimant:** Harmony Energy
*   **Asset:** Pillswood BESS (Pillswood 1 & 2)
*   **BM Unit IDs:** `E_PILLB-1` & `E_PILLB-2`
*   **Verbatim Claim:** 98 MW Export Capacity / 196 MWh Energy Capacity (2-hour duration)
*   **Pre-Registration Timeline:** Falsification/verification rules frozen in commit [`d6458e5`](https://github.com/VolMax-Studio/volmax-gb-bess-audit/commit/d6458e53995f32d3989c98ef2e3cf3426e2e5052) prior to acquiring the unseen window telemetry.
*   **Audit Window:** July 1, 2025 – June 30, 2026 (365 days)
    *   **Primary (Pre-registered, Unseen Window):** July 1, 2025 – May 31, 2026 (335 days)
    *   **Secondary (Prior Scoped Window):** June 1, 2026 – June 30, 2026 (30 days)
*   **Ground-Truth Anchor:** Elexon BMRS B1610 metered volumes (half-hourly billing telemetry)
*   **Final Verdict:**
    *   **Active Power Capacity (98 MW):** **Verified with Limitations (Bounded)**
    *   **Energy Storage Capacity (196 MWh):** **Verified with Limitations (Bounded)**

---

## 2. Resolution Floor & Measurement Boundaries

This audit is subject to the physical and technical resolution limits of the public Elexon BMRS B1610 database, which serves as the ground-truth anchor:

*   **Temporal Resolution Floor:** Metered volumes are archived in 30-minute settlement periods. Instantaneous grid-service spikes (e.g. sub-second response times or frequency containment delivery) cannot be observed or verified.
*   **Power Conversion Constraint:** Active export/import power (MW) is not measured directly by the anchor. It is computed as a 30-minute average rate:
    $$\text{Average Power (MW)} = \text{Metered Volume (MWh)} \times 2$$
    *Note: Because each settlement period is exactly 0.5 hours, multiplying metered energy (MWh) by two yields the average active power (MW) over that settlement period.*
*   **Excluded Transients:** Grid telemetry averages out all sub-period power fluctuations, meaning short-duration frequency services or sub-period ramps are below the resolution floor of this audit.

---

## 3. P10 Verification Trail

The audit progressed through the five ordered levels of the P10 protocol:

| Level | Status | Reason |
| :--- | :--- | :--- |
| **L0 Admissibility** | **PASS** | Claim is testable; ground-truth anchor is independent and has an open BMRS license. |
| **L1 Data Integrity** | **PASS (one gap)** | Telemetry dataset matches SHA-256 hash in `data_manifest.json`. One 24-hour gap is documented on 2026-06-27; the cause is not determinable from the dataset. |
| **L2 Physics Compliance** | **PASS** | AC-to-AC Round-Trip Efficiency (RTE) is bounded by thermodynamic limits: 86.51% (unseen window) and 87.30% (scoped window), which are within standard physical bounds. |
| **L3 Statistical Integrity**| **PASS** | Rules were frozen *before* data acquisition of the 11-month unseen window. Data leakage and retrofitting are prevented. |
| **L4 Reproducibility** | **PASS** | All findings regenerate deterministically using the `scratch/audit_pillswood_12m.py` script. |
| **L5 Final Verdict** | **Verified with Limitations** | Active power capability (98 MW) verified as **Bounded** at 97.78 MW. Energy capacity (196 MWh) is **Bounded** at 183.67 MWh; lack of SoC data prevents physical refutation. |

---

## 4. Quantitative Analysis & Metrics

The quantitative verification of the dataset yielded the following asset-level metrics:

### A. Operational Metrics (Split Windows)

| Parameter | Unseen Window (11 Months) | Scoped Window (June 2026) | Combined System (12 Months) |
| :--- | :---: | :---: | :---: |
| **Operating Days** | 335 Days | 29 Days | 364 Days |
| **Nameplate capacity (Combined)** | 99.8 MW | 99.8 MW | 99.8 MW |
| **Total Grid Charge** | 77,646.88 MWh | 8,348.45 MWh | 85,995.33 MWh |
| **Total Grid Discharge** | 67,169.07 MWh | 7,288.54 MWh | 74,457.62 MWh |
| **AC-to-AC RTE (Combined)** | **86.51%** | **87.30%** | **86.58%** |
| *-- Pillswood 1 (`E_PILLB-1`)* | *86.64%* | *87.61%* | *86.74%* |
| *-- Pillswood 2 (`E_PILLB-2`)* | *86.36%* | *87.00%* | *86.42%* |
| **Capacity Factor (CF)** | **8.52%** | **10.69%** | **8.70%** |
| **Daily Cycles** | **1.023 cycles/day** | **1.282 cycles/day** | **1.044 cycles/day** |

*Note: Operating Days are defined as the number of unique calendar days containing at least one non-zero telemetry record (charge or discharge) in the dataset. The single missing day (364 vs 365 days; 29 vs 30 days in June) represents a 24-hour telemetry gap on 2026-06-27; the cause is not determinable from the dataset.*

### B. Sub-Claim A: Active Power Capacity (98 MW Export)
*   **Pre-registered Target Threshold:** $\ge 98.0\text{ MW}$ export.
*   **Maximum Observed 30-Minute Average Export Power:**
    *   **Unseen Window (Primary):** **97.78 MW** (observed on 2026-03-31 SP35, representing a combined metered export volume of 48.89 MWh in a single 30-minute settlement period).
    *   **Scoped Window (Secondary):** **97.65 MW** (observed on 2026-06-20 SP41).
    *   **Combined 12-Month Period:** **97.78 MW**.
*   **Deviation from Claim:** $-0.22\text{ MW}$ ($-0.22\%$).
*   **Verdict:** **Verified with Limitations (Bounded)**.
    *   *Justification:* The maximum observed 30-minute average export power was 97.78 MW. Because it did not strictly meet or exceed the nameplate capacity of 98.0 MW, the capability is classified as **Bounded** by the maximum observed dispatch under the 30-minute resolution floor. While consistent with the claim (within 99.78% to account for metering tolerances and internal BESS auxiliary loads), the full nameplate capacity was not fully demonstrated.

### C. Sub-Claim B: Energy Capacity (196 MWh / 2-Hour Duration)
*   **Pre-registered Target Threshold:** $\ge 196.0\text{ MWh}$ export.
*   **Maximum Continuous Discharge Block:**
    *   **Unseen Window (Primary):** **183.67 MWh** over 4.5 hours (average export power of 40.82 MW), occurring on 2026-03-31 from Settlement Period 33 to 41.
    *   **Scoped Window (Secondary):** **177.90 MWh** over 3.5 hours (average export power of 50.83 MW), occurring on 2026-06-29 from Settlement Period 37 to 43.
    *   **Combined 12-Month Period:** **183.67 MWh** (on 2026-03-31).
*   **Top 5 Discharge Block Profiles (12-Month Combined):**
    1.  **183.67 MWh** (4.5h @ 40.82 MW average, 2026-03-31 SP33–41, Unseen Window)
    2.  **183.41 MWh** (6.5h @ 28.22 MW average, 2025-09-03 SP33–45, Unseen Window)
    3.  **181.89 MWh** (3.0h @ 60.63 MW average, 2026-05-30 SP39–44, Unseen Window)
    4.  **180.73 MWh** (4.5h @ 40.16 MW average, 2026-03-25 SP35–43, Unseen Window)
    5.  **180.50 MWh** (3.0h @ 60.17 MW average, 2026-05-09 SP37–42, Unseen Window)
*   **Verdict:** **Verified with Limitations (Bounded)**.
    *   *Justification:* The maximum observed continuous discharge block of 183.67 MWh represents 93.7% of the nominal 196 MWh capacity claim. Under the pre-registered verification rules, since State-of-Charge (SoC) telemetry is unobservable, shorter discharge blocks cannot refute the physical nominal capacity of the cells. The energy capacity is therefore verified as bounded by commercial market dispatch and the observation window.

### D. Settlement Run Revision (II vs. SF/R1)
The initial June 2026 scoping (run against the Initial Image / II settlement data) measured a maximum discharge block of **177.63 MWh** on June 20. The updated 12-month pull (utilizing mature SF/R1 runs) reveals a slightly higher block of **177.90 MWh** on June 29. This $+0.27\text{ MWh}$ ($+0.15\%$) delta is a direct physical signature of Elexon settlement run revisions as billing data matures, highlighting the necessity of the settlement-run caveat.

---

## 5. Key Limitations & Uncertainties

The verdict is qualified by the following structured limitations, in accordance with the P10 Caveat Theorem:

1.  **Temporal Resolution Floor:** Because B1610 telemetry is reported in half-hourly intervals, instantaneous sub-period spikes or transient grid-service delivery (e.g. sub-second frequency containment) cannot be verified. All active power ratings are testable only as 30-minute averages.
2.  **Market-Driven Dispatch Constraint:** BESS dispatch is optimized by market-driven dispatch (the operator's published case study attributes trading to Tesla Autobidder — see sources; not verifiable from B1610). It is not operated as a continuous physical capacity test. The maximum continuous discharge block of 183.67 MWh represents the maximum dispatched energy, not necessarily the physical boundary of the cells.
3.  **Energy Capacity Confirmation Gap:** The maximum observed discharge (183.67 MWh) represents 93.7% of the nominal 196 MWh claim. The discharge block terminated and was immediately followed by charging. This behavior is consistent with either market-driven dispatch optimization or depletion of the available state of charge. Public telemetry does not allow these explanations to be distinguished. Therefore, the dataset alone is sufficient to establish a lower bound of 183.67 MWh but cannot confirm nor refute the physical 196 MWh limit.
4.  **AC-to-AC RTE Boundary Caveat:** The annual AC-to-AC RTE of 86.58% is calculated over the entire 12-month window. Because State-of-Charge (SoC) telemetry is unobservable in B1610 data, we cannot perform initial/final state matching (state closing) on the battery capacity. The theoretical error bound introduced by this starting/ending SoC mismatch on the calculated RTE is given by the formula:
    $$\text{RTE Error Bound} = \pm \frac{E_{\text{cap}}}{C_{\text{total}}}$$
    Where $E_{\text{cap}} = 196\text{ MWh}$ is the maximum capacity of the BESS, and $C_{\text{total}}$ is the total charge throughput. For the unseen 11-month window ($C_{\text{total}} = 77,646.88\text{ MWh}$), this yields an error bound of $\pm 0.25$ percentage points. For the full 12-month window ($C_{\text{total}} = 85,995.33\text{ MWh}$), the error bound is $\pm 0.23$ percentage points. This indicates that the mismatch has a negligible impact on the calculated RTE over long windows, making it a stable descriptive metric of thermodynamic efficiency, though not a contract-compliance verdict carrier.

---

## 6. Recommendations for Subsequent Audits

To resolve the remaining energy capacity confirmation gap, we recommend:
1.  **Operator State-of-Charge (SoC) Integration:** If available under an updated data agreement, integrate operator SoC telemetry as a secondary anchor to measure cell-level depletion directly.
2.  **Grid Constraint Correlation:** Cross-reference operational dispatch periods with local grid export constraints to determine if discharge blocks were limited by grid capacity allocation rather than physical battery capacity.
