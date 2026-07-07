# P10 Verification Report: Pillswood BESS Grid-Dispatch Audit
### Report ID: `VM-2026-0002` | Protocol Version: `P10 v1.1`
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

This report presents the P10 verification sequence and final verdict for the active power and energy storage capacity claims of Harmony Energy's Pillswood BESS.

---

## 1. Executive Summary

*   **Claimant:** Harmony Energy
*   **Asset:** Pillswood BESS (Pillswood 1 & 2)
*   **BM Unit IDs:** `E_PILLB-1` & `E_PILLB-2`
*   **Verbatim Claim:** 98 MW Export Capacity / 196 MWh Energy Capacity (2-hour duration)
*   **Audit Period:** June 1, 2026 – June 30, 2026 (30 days)
*   **Ground-Truth Anchor:** Elexon BMRS B1610 metered volumes (half-hourly billing telemetry)
*   **Final Verdict:** **Verified with Limitations**

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
| **L1 Data Integrity** | **PASS** | Telemetry dataset matches SHA-256 hash in `data_manifest.json`. No missing values or timing drift. |
| **L2 Physics Compliance** | **PASS** | AC-to-AC Round-Trip Efficiency (RTE) is bounded by thermodynamic limits ($88.4\% - 89.1\%$). No anomalous self-charging or conservation law violations. |
| **L3 Statistical Integrity**| **PASS** | No data leakage or train/test contamination. Active power computed as half-hourly averages. |
| **L4 Reproducibility** | **PASS** | All findings regenerate deterministically using the provided `analyze_pillswood.py` script. |
| **L5 Final Verdict** | **Verified with Limitations** | Maximum observed 30-minute average export power was 97.65 MW. Energy duration verified up to 177.63 MWh; full 196 MWh cannot be confirmed nor refuted from June 2026 data alone. |

---

## 4. Quantitative Analysis & Metrics

The quantitative verification of the dataset yielded the following asset-level metrics:

### A. Operational Metrics (June 2026)

| Parameter | Pillswood 1 (`E_PILLB-1`) | Pillswood 2 (`E_PILLB-2`) | Combined System |
| :--- | :--- | :--- | :--- |
| **Nameplate Capacity** | 49.9 MW | 49.9 MW | 99.8 MW |
| **Total Grid Charge** | 3,894.22 MWh | 3,892.23 MWh | 7,786.45 MWh |
| **Total Grid Discharge** | 3,470.09 MWh | 3,441.56 MWh | 6,911.65 MWh |
| **AC-to-AC RTE** | **89.11%** | **88.42%** | **88.77%** |
| **Capacity Factor (CF)** | — | — | **9.80%** |
| **Daily Cycles** | — | — | **1.175 cycles/day** |
| **Telemetry Records** | 1,294 | 1,294 | 1,294 |

### B. Sub-Claim A: Active Power Capacity (98 MW Export)
*   **Maximum Observed 30-Minute Average Export Power:** **97.65 MW** (observed on 2026-06-20 SP41, representing a combined metered export volume of 48.825 MWh in a single 30-minute settlement period).
*   **Deviation from Claim:** $-0.35\text{ MW}$ ($-0.36\%$).
*   **Verdict:** **Verified**. The combined system successfully demonstrated sustained export power within 99.6% of the 98 MW claim.

### C. Sub-Claim B: Energy Capacity (196 MWh / 2-Hour Duration)
*   **Maximum Continuous Discharge Block:** **177.63 MWh** over 7.5 hours (average export power of 23.68 MW), occurring on 2026-06-20 from Settlement Period 33 to 47.
*   **Top Discharge Block Profiles:**
    1.  **177.63 MWh** (7.5h @ 23.68 MW average, 2026-06-20 SP33–47)
    2.  **169.80 MWh** (4.5h @ 37.73 MW average, 2026-06-21 SP37–45)
    3.  **167.16 MWh** (4.0h @ 41.79 MW average, 2026-06-07 SP35–42)
*   **Verdict:** **Verified with Limitations**.

### D. Asset Utilization & Dispatch Profile

#### 1. Utilization Histogram
Shows the total hours and percentage of active export time spent in each power range during June 2026:

| Power Range (MW) | Active Export Duration (Hours) | Percentage of Active Export Time |
| :--- | :--- | :--- |
| **0 – 10 MW** | 125.5 Hours | 43.20% |
| **10 – 30 MW** | 75.5 Hours | 25.99% |
| **30 – 60 MW** | 64.0 Hours | 22.03% |
| **60 – 90 MW** | 19.5 Hours | 6.71% |
| **> 90 MW** | 6.0 Hours | 2.07% |

#### 2. Dispatch Duration Curve Percentiles
Key percentiles of combined active power export when discharging:

*   **Maximum (100%):** 97.65 MW
*   **90th Percentile (P90):** 57.64 MW
*   **75th Percentile (P75):** 38.55 MW
*   **50th Percentile (Median):** 14.49 MW
*   **25th Percentile (P25):** 3.79 MW
*   **10th Percentile (P10):** 0.75 MW
*   **Minimum (0%):** 0.00 MW

---

## 5. Key Limitations & Uncertainties

The verdict is qualified by the following structured limitations, in accordance with the P10 Caveat Theorem:

1.  **Temporal Resolution Floor:** Because B1610 telemetry is reported in half-hourly intervals, instantaneous sub-period spikes or transient grid-service delivery (e.g. sub-second frequency containment) cannot be verified. All active power ratings are testable only as 30-minute averages.
2.  **Market-Driven Dispatch Constraint:** BESS dispatch is optimized by Tesla Autobidder to maximize wholesale arbitrage and ancillary services revenue. It is not operated as a continuous physical capacity test. The maximum continuous discharge block of 177.63 MWh represents the maximum dispatched energy, not necessarily the physical boundary of the cells.
3.  **Energy Capacity Confirmation Gap:** The maximum observed discharge (177.63 MWh) represents 90.6% of the nominal 196 MWh claim. The discharge block terminated and was immediately followed by charging. This behavior is consistent with either market-driven dispatch optimization or depletion of the available state of charge. Public telemetry does not allow these explanations to be distinguished. Therefore, the June 2026 dataset alone is sufficient to establish a lower bound of 177.63 MWh but cannot confirm nor refute the physical 196 MWh limit.

---

## 6. Recommendations for Subsequent Audits

To resolve the energy capacity confirmation gap, we recommend:
1.  **Extended Audit Window:** Expand the telemetry audit window to 6–12 months to capture seasonal peak-pricing periods or network stress events where sustained full-capacity discharge cycles are more likely to occur.
2.  **State-of-Charge (SoC) Integration:** If available under an updated data agreement, integrate operator SoC telemetry as a secondary anchor to measure cell-level depletion directly.
