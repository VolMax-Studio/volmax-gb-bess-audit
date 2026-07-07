# P10 Phase 3: Audit Preparation (UK-HARMONY-001)
### Pillswood BESS (98 MW / 196 MWh) Grid-Dispatch Audit

This document establishes the testable sub-claims, resolution floor constraints, and a-priori falsification rules for the Pillswood BESS grid-dispatch audit.

---

## 1. Asset Mapping & Identifiers

*   **Claim ID:** `UK-HARMONY-001`
*   **Asset Name:** Pillswood Battery Storage (Pillswood 1 & 2)
*   **Lead Operator:** Harmony Energy / BP Gas Marketing Limited (Trading Agent)
*   **Technology:** Tesla Megapack (2-hour duration lithium-ion)
*   **Software Optimizer:** Tesla Autobidder
*   **Balancing Mechanism Unit IDs:**
    *   `E_PILLB-1` (Pillswood 1 Battery Storage)
    *   `E_PILLB-2` (Pillswood 2 Battery Storage)
*   **Registered Capacities:**
    *   `E_PILLB-1`: 49.9 MW Export (Generation) / 49.9 MW Import (Demand)
    *   `E_PILLB-2`: 49.9 MW Export (Generation) / 49.9 MW Import (Demand)
    *   **Combined System Nameplate:** 99.8 MW Export / 99.8 MW Import

---

## 2. Claim Decomposition

To evaluate the verbatim claim of **98 MW power capacity** and **196 MWh energy capacity**, we decompose it into two distinct testable sub-claims:

### sub-claim A: Active Power Capacity (`UK-HARMONY-001a`)
*   **verbatim Statement:** *"98"* (MW export capacity)
*   **Hypothesis:** The combined system can sustain an export rate of 98 MW.
*   **Verification Anchor:** Elexon B1610 metered volumes.

### sub-claim B: Energy Storage Capacity (`UK-HARMONY-001b`)
*   **verbatim Statement:** *"196 (Lithium-ion)"* (MWh storage capacity / 2-hour duration)
*   **Hypothesis:** The combined system can store and discharge 196 MWh of energy in a single continuous cycle without intermediate charging.
*   **Verification Anchor:** Integrated Elexon B1610 metered volumes over continuous discharge blocks.

---

## 3. Resolution Floor Constraints

*   **Temporal Resolution:** B1610 metered volume is reported as half-hourly totals (MWh per 30-minute settlement period).
*   **Power Conversion:** Active power (MW) cannot be observed directly in real-time. It must be computed as an average rate over the 30-minute settlement period:
    $$\text{Average Power (MW)} = \text{Metered Volume (MWh)} \times 2$$
*   **Sub-Period Transient Exclusion:** Any sub-period fluctuations, sub-second response times, or frequency response delivery (e.g. Dynamic Containment) are completely below the 30-minute resolution floor and are excluded from this audit.

---

## 4. A-Priori Falsification Rules

Before executing any analytical script, we define the strict boundaries that would refute or limit the claims:

### Rule A: Active Power Falsification
1.  **Refutation Boundary:** If the combined metered volume in any single settlement period exceeds the physical registry limit of $99.8\text{ MW} \times 0.5\text{ h} = 49.9\text{ MWh}$ by more than a 5% measurement tolerance ($> 52.4\text{ MWh}$), the dataset contains a critical telemetry sign or scale error, refuting L1 Data Integrity.
2.  **Verification Boundary:** If the combined average power sustained over any 30-minute settlement period is $\ge 98\text{ MW} \times 0.95 = 93.1\text{ MW}$, the power capacity claim is verified.

### Rule B: Energy Capacity Falsification
1.  **Refutation Boundary:** If we observe a continuous discharge block (a contiguous sequence of settlement periods with positive metered volumes and no charging periods) that terminates due to physical depletion (indicated by subsequent zero or near-zero export) and yields significantly less than 196 MWh (e.g. $< 180\text{ MWh}$), the capacity claim is **refuted**.
2.  **Neutral Observation Boundary:** BESS systems are commercially operated under Autobidder to maximize revenue, not to run physical capacity tests. Therefore, if the maximum continuous discharge block observed in the 30-day dataset is less than 196 MWh (e.g. 158 MWh) but does *not* terminate due to BESS depletion (i.e. the discharge is terminated by market prices or instructions, leaving the BESS with residual charge), the nominal capacity cannot be refuted. The verdict in this case must be **Verified with Limitations**, noting that the physical capacity limit is bounded by market dispatch and recommending a wider audit window (6-12 months).
