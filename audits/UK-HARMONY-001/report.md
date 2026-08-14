# P10 Verification Report: Pillswood BESS Grid-Dispatch Audit
### Report ID: `VM-2026-0002` | Protocol Version: `P10 v1.1` | Document Version: `v2.4`
**Claim ID:** `UK-HARMONY-001` (Pillswood Battery Storage)

```yaml
Measurement Anchor:
  Dataset: Elexon BMRS B1610
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
*   **Trading Agent:** BP Gas Marketing Limited (BM Unit registered trading entity; non-claimant)
*   **Asset:** Pillswood BESS (Pillswood 1 & 2)
*   **BM Unit IDs:** `E_PILLB-1` & `E_PILLB-2`
*   **Verbatim Claim:** 98 MW Export Capacity / 196 MWh Energy Capacity (2-hour duration)
*   **Asset Energisation Date:** November 2022 (stated on case study page as "energised November 2022")
*   **Canonical Primary Claim URL:** [`https://harmonyenergy.co.uk/case-studies/pillswood-bess/`](https://harmonyenergy.co.uk/case-studies/pillswood-bess/) (Active, HTTP 200 OK as of 2026-08-14)
*   **Pre-Registered Wayback Archive Snapshot (Frozen Pre-Registration Anchor):** [`web.archive.org/web/20260707134620`](https://web.archive.org/web/20260707134620/https://harmonyenergy.co.uk/case-studies/pillswood-bess/) (Snapshot Timestamp `20260707134620`, verified opened HTTP 200 OK)
*   **Claim Evidence File:** Local evidence snapshot `evidence_claim.png` pinned in `audits/UK-HARMONY-001/`
*   **Package License & Scope Notice:** Layered licensing defined in `NOTICE` (CC BY 4.0 for report/findings/charts, MIT License for `reproduce.py`, BSC Public Data Licence for `raw_pillswood_12m.json` and third-party screenshot `evidence_claim.png` excluded from CC BY 4.0 grant; verbatim legal code in `LICENSE`).
*   **Pre-Registration Timeline:** Falsification/verification rules frozen in commit [`d6458e5`](https://github.com/VolMax-Studio/volmax-gb-bess-audit/commit/d6458e53995f32d3989c98ef2e3cf3426e2e5052) (Wed Jul 8 06:35:29 2026 UTC) prior to acquiring the unseen window telemetry (commit [`237e0c1`](https://github.com/VolMax-Studio/volmax-gb-bess-audit/commit/237e0c1)).
*   **Audit Window:** July 1, 2025 – June 30, 2026 (365 calendar days)
    *   **Primary (Pre-registered, Unseen Window):** July 1, 2025 – May 31, 2026 (335 days)
    *   **Secondary (Prior Scoped Window):** June 1, 2026 – June 30, 2026 (30 calendar days; 29 operating days due to documented 24h gap on 2026-06-27)
*   **Ground-Truth Anchor:** Elexon BMRS B1610 metered volumes (half-hourly billing telemetry, II/SF settlement runs)
*   **Reviewer:** Nestorov, Ivan / VolMax Studio Lab / ORCID 0009-0006-7940-9539
*   **Verdicts (Mapped Verbatim from Frozen Rule Grammar):**
    *   **Active Power Capacity (`UK-HARMONY-001a` — 98 MW):** **`Demonstrated`** (Rule A.1 satisfied: 97.78 MW 30-min settlement period average rate $\ge 93.1\text{ MW}$ threshold). Confidence: **High**.
    *   **Energy Storage Capacity (`UK-HARMONY-001b` — 196 MWh):** **`Bounded`** $\rightarrow$ **`Verified with Limitations`** (Rule B.2 satisfied: Maximum continuous discharge block of 183.67 MWh $< 186.2\text{ MWh}$ threshold under commercial market dispatch, yielding "Verified with Limitations" per frozen Rule B.2 text; unobservable SoC precludes physical hardware refutation). Confidence: **Moderate**.

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

The audit progressed through Stage 0 plus five ordered levels of the P10 v1.1 protocol (L0–L5):

| Level | Status | Reason / Evidence |
| :--- | :--- | :--- |
| **L0 Admissibility** | **PASS** | 5/5 criteria met; Elexon BMRS anchor & license verified. Layered scope defined in `NOTICE` (verbatim CC BY 4.0 in `LICENSE`). Snapshot opened at timestamp `20260707134620` on `/case-studies/pillswood-bess/`. |
| **L1 Data Integrity** | **PASS** | Both raw telemetry datasets match SHA-256 hashes in `data_manifest.json` (`raw_pillswood_12m.json`: `10ad081e...`; `raw_b1610_202606.json`: `6fc637c9...`). Gaps fully reconciled: 24h gap on 2026-06-27 (96 records) and 4 records on 2025-07-01 SP 1–2 (BST query boundary artifact). |
| **L2 Physics Compliance** | **PASS** | AC-to-AC Round-Trip Efficiency (RTE) = 86.51% (unseen window) and 87.30% (scoped window), within physical bounds $[0.60, 0.92]$. Rule A Clause 4 executed: Max single SP metered volume = 48.89 MWh ($< 49.90\text{ MWh}$ connection limit and $< 52.4\text{ MWh}$ threshold; zero physical data violation). |
| **L3 Statistical Integrity**| **PASS** | Rules frozen in commit `d6458e5` (2026-07-08) prior to data acquisition (`237e0c1`). High-level verdict string mapping aligned in v1.3/v1.4 to match frozen rule grammar verbatim (tracked in `versions.md`). |
| **L4 Reproducibility** | **PASS** | Single entry point `python3 reproduce.py` deterministically regenerates primary 12-month asset findings into `metrics_12m.json` (SHA-256: `b3958982...`) and secondary June 2026 scoped asset metrics into `metrics.json` (SHA-256: `e141a998...`) from frozen telemetry. External verification via `sha256sum -c SHA256SUMS` passes with 0 numeric diff. |
| **L5 Final Verdict** | **DECOMPOSED** | **Sub-claim A (Power 98 MW): `Demonstrated`** (97.78 MW 30-min settlement period average rate $\ge 93.1\text{ MW}$).<br>**Sub-claim B (Energy 196 MWh): `Bounded` $\rightarrow$ `Verified with Limitations`** (183.67 MWh max block $< 186.2\text{ MWh}$; 2h full-rate discharge profile unexercised; unobservable SoC prevents physical refutation). |

---

## 4. Quantitative Analysis & Metrics

The quantitative verification of the dataset yielded the following asset-level metrics:

### A. Operational Metrics (Split Windows) — *Descriptive Context Only*
*Note: Per-unit RTE, Capacity Factor, and Daily Cycles are reported below as descriptive operational context and carry zero verdict weight for L5 claim evaluation (mitigating PG9 risk).*

| Parameter | Unseen Window (11 Months) | Scoped Window (June 2026) | Combined System (12 Months) |
| :--- | :---: | :---: | :---: |
| **Operating Days** | 335 Days | 29 Operating Days (30 cal days; 24h gap on 2026-06-27) | 364 Days |
| **Grid Connection Nameplate (Combined BMU)** | 99.8 MW | 99.8 MW | 99.8 MW |
| **Commercial Claim Nameplate** | 98.0 MW | 98.0 MW | 98.0 MW |
| **Total Grid Charge** | 77,646.88 MWh | 8,348.45 MWh | 85,995.33 MWh |
| **Total Grid Discharge** | 67,169.07 MWh | 7,288.54 MWh | 74,457.62 MWh |
| **AC-to-AC RTE (Combined)** | **86.51%** | **87.30%** | **86.58%** |
| *-- Pillswood 1 (`E_PILLB-1`)* | *86.64%* | *87.61%* | *86.74%* |
| *-- Pillswood 2 (`E_PILLB-2`)* | *86.36%* | *87.00%* | *86.42%* |
| **Capacity Factor (vs 98.0 MW Claim)** | **8.52%** | **10.69%** | **8.70%** |
| **Capacity Factor (vs 99.8 MW Connection)** | **8.37%** | **10.49%** | **8.54%** |
| **Daily Cycles (vs 196 MWh Nominal)** | **1.023 cycles/day** | **1.282 cycles/day** | **1.044 cycles/day** |

---

### B. Sub-Claim A: Active Power Capacity (`UK-HARMONY-001a` — 98 MW Export)
*   **Pre-registered Target Threshold:** $\ge 98.0\text{ MW} \times 0.95 = 93.1\text{ MW}$ export.
*   **Maximum Observed 30-Minute Average Export Power:**
    *   **Unseen Window (Primary):** **97.78 MW** (observed on 2026-03-31 SP35, representing a combined metered export volume of 48.89 MWh in a single 30-minute settlement period).
    *   **Scoped Window (Secondary):** **97.65 MW** (observed on 2026-06-20 SP41).
    *   **Combined 12-Month Period:** **97.78 MW**.
*   **Deviation from 98.0 MW Commercial Claim:** $-0.22\text{ MW}$ ($-0.22\%$).
*   **Verdict:** **`Demonstrated`** (Confidence: **High**).
    *   *Justification:* Rule A.1 is satisfied. The maximum observed 30-minute average export power of 97.78 MW exceeds the pre-registered 93.1 MW verification threshold. Demonstrated at least 97.78 MW as a 30-minute settlement period average rate (representing 99.78% of nominal 98.0 MW commercial claim capacity after accounting for internal auxiliary loads and metering tolerances).

---

### C. Sub-Claim B: Active Energy Storage Capacity (`UK-HARMONY-001b` — 196 MWh)
*   **Pre-registered Target Threshold:** $\ge 196.0\text{ MWh} \times 0.95 = 186.2\text{ MWh}$ export.
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
*   **2-Hour Duration Profile Qualification:** The verbatim claim specifies a 2-hour duration (discharging 98 MW continuously for 2.0 hours). The top observed discharge blocks (6.5h, 4.5h, 3.0h) were all delivered at lower average power rates ($\le 60.63\text{ MW}$). A continuous 2-hour discharge block at or near the 98 MW nameplate rate was NOT exercised in public commercial telemetry.
*   **Verdict:** **`Bounded`** $\rightarrow$ **`Verified with Limitations`** (Confidence: **Moderate**).
    *   *Justification:* Rule B.2 is satisfied. The maximum observed continuous discharge block of 183.67 MWh fell below the pre-registered 186.2 MWh threshold (representing 93.7% of the nominal 196 MWh claim). Per frozen Rule B.2 text, because State-of-Charge (SoC) telemetry is unobservable in public Elexon B1610 telemetry, shorter discharge blocks under commercial market dispatch do NOT refute physical battery hardware capacity. Instead, the classification is `Bounded`, yielding a verdict of `Verified with Limitations`.

---

## 5. Key Limitations & Uncertainties

The verdict is qualified by the following structured limitations:

1.  **Exploratory Sensitivity Note on AC vs DC Capacity Boundary Assumptions:**
    *   *Boundary Sensitivity Analysis:* The pre-registered threshold was fixed at $95\% \times 196\text{ MWh} = 186.2\text{ MWh}$ at the AC connection boundary. Depending on whether 196 MWh refers to nominal DC cell capacity or usable AC grid boundary capacity, and depending on one-way discharge efficiency ($\eta_{\text{dis}}$), the theoretical expected AC discharge from a full cycle varies as follows:

    | Capacity Assumption | One-Way Discharge Efficiency ($\eta_{\text{dis}}$) | Expected AC Discharge | Ratio of Measured Block (183.67 MWh) to Expected |
    | :--- | :--- | :--- | :--- |
    | **196 MWh DC Cell** | $\eta_{\text{dis}} = \sqrt{0.8658} = 0.9305$ (Symmetric RTE) | **182.37 MWh AC** | **100.7%** |
    | **196 MWh DC Cell** | $\eta_{\text{dis}} = 0.9500$ (High-Efficiency Inverter/Transformer) | **186.20 MWh AC** | **98.6%** |
    | **196 MWh DC Cell** | $\eta_{\text{dis}} = 0.9700$ (Minimal Inverter Loss) | **190.12 MWh AC** | **96.6%** |
    | **196 MWh Usable AC** | N/A (Direct AC Boundary Rating) | **196.00 MWh AC** | **93.7%** |

    *   *Methodological Note:* Because public B1610 telemetry measures net AC settlement volumes rather than internal DC battery state, this audit does not make physical assertions regarding internal battery cell health or inverter topology. The verdict remains strictly `Bounded` as defined by pre-registered Rule B.2.
2.  **Settlement Run Lifecycle Stage:** The frozen telemetry databases (`raw_pillswood_12m.json` and `raw_b1610_202606.json`) consist of Initial Image (II) and Final Settlement (SF) runs from Elexon BMRS. B1610 metered volumes undergo multi-stage BSC settlement reconciliations (SF, R1, R2, R3, RF over ~14 months). The observed $+0.27\text{ MWh}$ delta between II and SF data (measured on the June 2026 scoped dataset) demonstrates that metrics remain subject to future settlement run revisions.
3.  **Temporal Resolution Floor:** Because B1610 telemetry is reported in half-hourly intervals, instantaneous sub-period spikes or transient grid-service delivery (e.g. sub-second frequency containment) cannot be verified. All active power ratings are testable only as 30-minute settlement period averages.
4.  **Commercial Market Dispatch vs Physical Capacity:** BESS dispatch is optimized by commercial market dispatch (Tesla Autobidder). It is not operated as a continuous physical capacity test. The maximum continuous discharge block of 183.67 MWh represents a lower bound on exercised capacity under commercial market dispatch, not a physical refutation of nominal cell capacity.
5.  **AC-to-AC RTE Boundary Error Bound:** The annual AC-to-AC RTE of 86.58% is calculated over the 12-month window. Unobservable starting/ending State-of-Charge (SoC) introduces a theoretical error bound of $\pm \frac{E_{\text{cap}}}{C_{\text{total}}} = \pm \frac{196}{85,995} = \pm 0.23$ percentage points (where $E_{\text{cap}} = 196\text{ MWh}$ nominal claim capacity and $C_{\text{total}} = 85,995\text{ MWh}$ total AC grid charge throughput), making RTE a stable descriptive metric of thermodynamic efficiency.
6.  **Governance Exception Note (PG8 vs Anole Data Rule):** Primary unseen raw telemetry `raw_pillswood_12m.json` (9 MB) is included directly within the audit directory under Elexon BMRS worldwide royalty-free redistributable terms, satisfying PG8 (*"Raw data is inside the archive"*). Secondary fleet telemetry `raw_b1610_202606.json` (171k records) is retained externally and pinned via SHA-256 hash in `data_manifest.json` because it contains raw 30-day telemetry for 137 third-party GB fleet BM units that are NOT the subject of this asset audit (`UK-HARMONY-001`). Keeping third-party fleet telemetry outside the audit directory avoids polluting the asset archive with un-audited third-party fleet data.

---

## 6. Audit Summary & Signature Table

```markdown
| Level | Status | Evidence / Result |
|:---|:---|:---|
| **L0 Admissibility** | PASS | 5/5 criteria met; Elexon anchor verified; layered scope defined in NOTICE (verbatim CC BY in LICENSE). Snapshot opened at timestamp 20260707134620 on /case-studies/pillswood-bess/ |
| **L1 Data Integrity** | PASS | SHA-256 matches manifest (`raw_pillswood_12m.json`: `10ad081e...`, `raw_b1610_202606.json`: `6fc637c9...`) |
| **L2 Physics Compliance** | PASS | AC-to-AC RTE = 86.58% (in bounds [0.60, 0.92]). Max SP volume = 48.89 MWh (< 49.90 MWh limit) |
| **L3 Statistical Integrity** | PASS | Rules frozen in commit `d6458e5` (2026-07-08) before data acquisition (`237e0c1`). Alignment in v1.3/v1.4 tracked in versions.md |
| **L4 Reproducibility** | PASS | Single entry point `python3 reproduce.py` deterministically regenerates primary `metrics_12m.json` (SHA-256: `b3958982...`) and secondary `metrics.json` (SHA-256: `e141a998...`) from raw telemetry |
| **L5 Final Verdict** | **DECOMPOSED** | **Sub-claim A (Power 98 MW): `Demonstrated`** (High confidence)<br>**Sub-claim B (Energy 196 MWh): `Bounded` $\rightarrow$ `Verified with Limitations`** (Moderate confidence) |
```

---

*VolMax Studio Lab · P10 Verification Audit Report (`VM-2026-0002`)*
*Reviewer: Nestorov, Ivan / VolMax Studio Lab / ORCID 0009-0006-7940-9539*
