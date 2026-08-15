# P10 Reproduction Criterion (UK-HARMONY-001)
**Protocol Version:** `P10 v1.1` | **Target Audit ID:** `VM-2026-0002` | **Target Commit:** `067e017` | **Criterion Version:** `v1.0`

---

## 1. Purpose & Scope

This document establishes pre-registered normative criteria for classifying third-party reproductions of the **Pillswood BESS Capacity Audit (`UK-HARMONY-001` v2.4)**. 

To eliminate post-hoc interpretation and rule-bending, this criterion defines exact execution conditions, boundary requirements, negative test procedures, and allowed public verdict vocabulary prior to external execution.

---

## 2. Independent Third-Party Definition

An **Independent Third-Party Executor** is defined strictly as:
1. A named individual or organization external to VolMax Studio.
2. Operating independently (not under direction, employment, or contract with VolMax Studio).
3. Leaving a publicly auditable trace (such as a GitHub Issue or public comment containing raw terminal logs, cryptographic hashes, and command exit status).

*Note: Executions performed by VolMax Studio team members, automated internal CI agents, or pair-programming AI assistants do not constitute third-party reproduction.*

---

## 3. Level 1 — Package Reproduction

A **Level 1 Package Reproduction** verifies that an independent third party can execute the published audit package against frozen telemetry archives and deterministically re-create identical results.

### 3.1 Execution Environment
* Python 3.8+ using **Standard Library Only** (referencing `versions.md §3`). No third-party `pip` dependencies are permitted for core audit reproduction.

### 3.2 Verification Procedure (< 5 Minutes)
To perform a complete Level 1 verification:
```bash
git clone https://github.com/VolMax-Studio/volmax-gb-bess-audit
cd volmax-gb-bess-audit/audits/UK-HARMONY-001
sha256sum -c SHA256SUMS
python3 reproduce.py
```

### 3.3 Success Conditions
Level 1 verification is successful if and only if **all five** of the following conditions are met:
1. **Cryptographic Manifest Integrity:** `sha256sum -c SHA256SUMS` returns `OK` for all 15 pinned package artifacts.
2. **Deterministic Re-creation:** `reproduce.py` completes with exit status `0`.
3. **Byte-Identity:** The generated `metrics.json` file matches the baseline SHA-256 hash `e141a998d91ef0154fccc047429f476f7ddcd4e78fbc532f35c38f3ca46b3148` (0 numeric diff). The non-deterministic field set for version v2.4 is explicitly empty.
4. **Primary Metric Identity:** Generated `metrics_12m.json` matches baseline SHA-256 hash `b3958982001b1fb9f3594559a657177a1bf6e7a8079b296cbced68d018c0513a`.
5. **Negative Fault Injection Test:** 
   - The executor modifies 1 byte in `raw_pillswood_12m.json`.
   - `python3 reproduce.py` detects the SHA-256 mismatch against `data_manifest.json`, prints error output, and halts with exit status `exit ≠ 0`.
   - The executor restores `raw_pillswood_12m.json` via `git checkout raw_pillswood_12m.json`.

### 3.4 Allowed Public Verdict Vocabulary (Level 1)
Upon meeting all conditions above, the execution must be cited exclusively as:
> **`independently executed (package reproduction)`**

It must **not** be cited as a "method reproduction" or "independent method validation".

---

## 4. Level 2 — Method Reproduction

A **Level 2 Method Reproduction** independently reconstructs the evaluation from raw Elexon BMRS telemetry without using VolMax-derived JSON metrics or script artifacts as input.

### 4.1 Requirements for Level 2 Execution
The independent executor must:
1. Independently pull raw B1610 telemetry for BM Units `E_PILLB-1` and `E_PILLB-2` directly from Elexon BMRS (`https://bmrs.elexon.co.uk/`).
2. Document the specific Elexon settlement run/revision (e.g., II, SF, R1, R2, R3, RF, DF) of the retrieved dataset.
3. Reconstruct the 12-month metrics following the rules frozen in `report.md` and commit `d6458e5`.

### 4.2 Settlement Drift & Tolerance Rule
Because Elexon metered volumes are revised across multi-year settlement runs, a numerical discrepancy between an independent Elexon pull and the frozen telemetry archive is not automatically a methodological failure.

**Strict Pre-Registration Rule:** Until explicit quantitative numerical tolerance bounds for settlement drift are pre-registered and frozen in a git commit, any Level 2 execution yielding numerical differences **must be classified as `discrepancy — unclassified`**. It cannot be declared a pass or failure until the discrepancy is formally classified against:
* Elexon settlement run revision;
* Input telemetry boundary definitions;
* Execution environment;
* Rule implementation.

### 4.3 Allowed Public Verdict Vocabulary (Level 2)
Upon successful reconstruction meeting pre-registered tolerances:
> **`independently reproduced (method reproduction)`**

---

## 5. Summary of Allowed Verdict Vocabulary

Only the following closed set of verdict labels may be assigned to any external execution report:
* `independently executed (package reproduction)` — Level 1 package & script verification.
* `independently reproduced (method reproduction)` — Level 2 independent data & method reconstruction.
* `discrepancy — unclassified` — Execution yielding numerical or environment differences pending classification.

---

## 6. Pre-Registration Anchor

This criterion document is an integral component of the `UK-HARMONY-001` v2.4 audit package. Its Git commit timestamp serves as the objective cryptographic anchor establishing that these rules were published and frozen before any external third-party execution attempt.
