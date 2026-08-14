# Environment & Dependency Lock (UK-HARMONY-001)

This audit was executed in a minimal environment relying exclusively on standard Python library components.

## 1. Operating System
*   **OS:** Linux (Ubuntu 24.04 LTS / Debian-based)
*   **Kernel:** x86_64 Linux

## 2. Runtimes
*   **Python:** 3.12.3 (GCC 13.3.0)

## 3. Library Dependencies
*   **Standard Libraries Only:** No external pip packages (such as `pandas`, `numpy`, or `scipy`) are required to run the verification pipeline, ensuring zero dependency decay over time.
*   **Standard imports utilized:**
    *   `os` (system path utilities)
    *   `sys` (runtime environment hooks)
    *   `json` (data parsing)
    *   `hashlib` (SHA-256 integrity calculation)
    *   `argparse` (CLI parsing)

## 4. Document Changelog
*   **v1.0 (2026-07-08):** Initial 30-day scoped audit prep and pre-registration freeze (`d6458e5`).
*   **v1.1 (2026-07-09):** 12-month unseen window data acquisition (`237e0c1`) and analysis.
*   **v1.2 (2026-08-12):** P10 Governance Gate remediation: decomposed verdicts (`Verified` / `Not Demonstrated`), dual raw telemetry manifest pinning (`raw_pillswood_12m.json` + `raw_b1610_202606.json`), exact ORCID reviewer lock (`Nestorov, Ivan / VolMax Studio Lab / ORCID 0009-0006-7940-9539`), 2-hour duration sub-claim explicit qualification, and dual nameplate separation.
*   **v1.3 (2026-08-12):** P10 Round 2 Governance Gate remediation: restored verbatim frozen rule grammar (`Demonstrated` for Rule A; `Bounded` $\rightarrow$ `Verified with Limitations` for Rule B), added DC$\to$AC threshold conversion self-audit limitation (§5.1), single claimant lock (`Harmony Energy`), and executed Rule A Clause 4 L2 physical check.
*   **v1.4 (2026-08-12):** P10 Round 3 Governance Gate remediation: reframed §5.1 as an exploratory AC/DC boundary sensitivity note with full sensitivity matrix (eliminating unhedged hardware assertions), standardized protocol version to `P10 v1.1`, explicit `metrics.json` citation in L4 row (`b3958982...`), updated decision log date to `2026-08-12`, and aligned sub-claim B label (`196 MWh`).
*   **v1.5 (2026-08-12):** P10 Round 4 Governance Gate remediation: pinned verbatim claim source URL, publication date (Nov 2022), Wayback Machine snapshot (`20260707142812`), local evidence screenshot reference (`evidence_claim.png`), updated Stage 0 phrasing in §3, and sanitized remaining language artifacts.
*   **v1.6 (2026-08-12):** P10 Round 5 Governance Gate remediation: explicit `metrics_12m.json` SHA-256 key assignment (`b3958982...`), standardized claim source URL and archive snapshot, added dedicated `LICENSE` file (CC BY 4.0, MIT, and un-elided Elexon BSC licence), and added explicit PG8 vs Anole Data Rule exception note (§5.6).
*   **v1.7 (2026-08-13):** P10 Round 6 Governance Gate remediation: replaced hybrid LICENSE with official verbatim Creative Commons Attribution 4.0 International Public License (149 lines), opened and verified Wayback Machine snapshot timestamp `20260707134620` on `/case-studies/pillswood-bess/` (confirming `98 / 196 (Lithium-ion)` MW/MWH claim and asset energisation date November 2022), preserved verbatim `[year]` placeholder in Elexon BSC license template text, updated §5.6 exception justification (137 third-party fleet units kept outside asset archive to prevent volume bloat and cross-unit data pollution), and clarified pipeline execution roles for primary `metrics_12m.json` vs secondary `metrics.json`.
*   **v1.8 (2026-08-13):** P10 Round 7 Governance Gate remediation: added dedicated NOTICE file (`audits/UK-HARMONY-001/NOTICE`) establishing explicit 3-part layered license scope boundaries (CC BY 4.0 for reports/findings, MIT License for verification code `reproduce.py`, and Elexon BSC Public Data Licence for raw telemetry `raw_pillswood_12m.json` explicitly excluded from VolMax CC BY 4.0 grant), satisfying PG5 rule without altering verbatim legal code in `LICENSE`.
*   **v1.9 (2026-08-13):** P10 Round 8 Governance Gate remediation: established single entry point `python3 reproduce.py` to deterministically regenerate both primary `metrics_12m.json` and secondary `metrics.json` (resolving I1 blocker); updated `NOTICE` to explicitly categorize PNG files (`pillswood_discharge_block.png` under CC BY 4.0, third-party claim screenshot `evidence_claim.png` excluded from VolMax CC BY 4.0 grant); cited `NOTICE` across `report.md` §1 Executive Summary and L0/L4 tables; executed formal PREPUBLISH_CHECKLIST PG1–PG9 verification pass (including PG6 credential grep and PG7 link/path checks).
*   **v2.0 (2026-08-13):** P10 Round 9 Governance Gate remediation: aligned `reproduce.py` pipeline to deterministically emit the exact canonical `metrics_12m.json` (`b3958982...`) from `raw_pillswood_12m.json` with 0 numeric diff (resolving J1 blocker); removed auto-bootstrap fallback in `verify_data_integrity()` to strictly enforce `sys.exit(1)` on missing manifest or hash mismatch (resolving J2 blocker); ensured full CWD independence for `reproduce.py` execution across all working directories (resolving J3 blocker); executed full PG7 link resolution and HTTP status checks (confirming Wayback archive snapshot `20260707134620` HTTP 200 OK); executed PG6 second grep sweep for circumvention/vpn/proxy terms (0 matches in audit documentation); explicitly marked PG9 as SKIPPED pending final human public announcement draft.
*   **v2.1 (2026-08-13):** P10 Round 10 Governance Gate remediation: corrected `data_manifest.json` SHA-256 in `SHA256SUMS` (`fb5162b8...`, resolving K1 blocker); removed internal expected hash constants from `reproduce.py` to eliminate self-referential tautology and enforce pure external validation via `sha256sum -c` (resolving K2 blocker); enabled full deterministic regeneration of metrics from telemetry (resolving K3 blocker); corrected misleading "fleet" labeling of `metrics.json` to "secondary June 2026 scoped asset metrics" across `report.md` and `decision_log.json` (resolving K4 blocker); updated original claim URL in `sources.md` and `report.md` to document offline HTTP 404 status while confirming Wayback snapshot `20260707134620` (HTTP 200 OK) as the sole active ground-truth evidence anchor (resolving K5 blocker).
*   **v2.2 (2026-08-13):** P10 Round 11 Governance Gate remediation: enabled full deterministic calculation and emission of secondary June 2026 scoped asset metrics `metrics.json` directly from `raw_pillswood_12m.json` in `reproduce.py` (SHA-256: `e141a998...`, resolving L1 blocker); synchronized all L4 reproducibility citations across `report.md` (§3 and §6), `reproduce.py` docstring, and `versions.md` to state that both `metrics_12m.json` and `metrics.json` deterministically regenerate from frozen telemetry; updated `sources.md` Elexon entry to active portal `https://bmrs.elexon.co.uk/` (verified HTTP 200 OK).
*   **v2.4 (2026-08-14):** P10 Independent Audit Remediation: corrected canonical primary claim URL pointer in `sources.md` and `report.md` to non-`www` host `https://harmonyenergy.co.uk/case-studies/pillswood-bess/` (verified active HTTP 200 OK as of 2026-08-14), retaining pre-registered Wayback snapshot `20260707134620` as frozen pre-registration evidence anchor (resolving Check 9 / PG7 pointer blocker).








