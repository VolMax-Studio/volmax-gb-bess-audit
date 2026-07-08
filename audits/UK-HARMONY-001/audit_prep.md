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

## 4. A-Priori Falsification & Verification Rules

These rules are formally pre-registered and fixed after the scoping of June 2026 data, but prior to the acquisition and analysis of the remaining 11-month window (July 2025 – May 2026).

### Rule A: Active Power Verification Grammar
The active power capacity claim ($P_{\text{claim}} = 98\text{ MW}$) is evaluated using the following classification grammar:
1.  **Demonstrated**: Verified if the combined average power sustained over any 30-minute settlement period is $\ge 98\text{ MW} \times 0.95 = 93.1\text{ MW}$.
2.  **Bounded**: Classified as bounded if the maximum combined average power sustained over any 30-minute settlement period is $P_{\text{max}} < 93.1\text{ MW}$, indicating that the full capacity was not fully dispatched or required by market conditions in the window.
3.  **Not Exercised**: Classified as not exercised in the window if no active export is recorded.
4.  *Physical/Data Violations*: If the combined metered volume in any single settlement period exceeds the physical grid connection limit of $99.8\text{ MW} \times 0.5\text{ h} = 49.9\text{ MWh}$ by more than a 5% measurement tolerance ($> 52.4\text{ MWh}$), this opens an L2 physical anomaly (data/telemetry error) rather than refuting the capacity claim itself.

### Rule B: Energy Capacity Verification Grammar
The energy storage capacity claim ($E_{\text{claim}} = 196\text{ MWh}$) is evaluated using the following classification grammar:
1.  **Demonstrated**: Verified if a continuous discharge block (a contiguous sequence of settlement periods with positive metered volumes and no charging periods) yields $\ge 196\text{ MWh} \times 0.95 = 186.2\text{ MWh}$ at the AC connection boundary.
2.  **Bounded**: Classified as bounded by the observation window and market dispatch if the maximum continuous discharge block observed is $E_{\text{max}} < 186.2\text{ MWh}$. Because State-of-Charge (SoC) telemetry is not available in public Elexon B1610 data (meaning zero import does not prove the battery was full, and zero export does not prove it was empty), shorter cycles cannot physically refute the nominal storage capacity. Instead, $E_{\text{max}}$ is a descriptive lower bound on the exercised capacity under commercial market dispatch, yielding a verdict of "Verified with Limitations".
3.  **Not Exercised**: Classified as not exercised if no significant discharge blocks are observed.
