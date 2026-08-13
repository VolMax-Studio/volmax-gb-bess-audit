#!/usr/bin/env python3
"""
reproduce.py
Offline verification pipeline for the GB BESS Audit (UK-HARMONY-001 / VM-2026-0002).
Single entry point for deterministically regenerating primary 12-month asset metrics (metrics_12m.json)
and secondary June 2026 scoped asset metrics (metrics.json) from frozen telemetry archives using Python Standard Library only.
"""

import os
import sys
import json
import hashlib
import argparse

def calculate_sha256(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            sha256.update(chunk)
    return sha256.hexdigest()

def find_file(filename):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(os.getcwd(), filename),
        os.path.join(script_dir, filename),
        os.path.join(script_dir, "audits", "UK-HARMONY-001", filename),
        os.path.abspath(filename)
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None

def verify_data_integrity(data_path, manifest_path):
    print("--- Level 1 & 4 Integrity Check: P10 Data Pinning ---")
    if not data_path or not os.path.exists(data_path):
        print(f"CRITICAL ERROR: Raw data file '{data_path}' not found.")
        print("P10-L1 Integrity check FAILED. Aborting execution.")
        sys.exit(1)
        
    actual_hash = calculate_sha256(data_path)
    print(f"Actual SHA-256 of '{os.path.basename(data_path)}': {actual_hash}")
    
    if not manifest_path or not os.path.exists(manifest_path):
        print(f"CRITICAL ERROR: Manifest file '{manifest_path}' not found.")
        print("P10-L4 Integrity check FAILED. Aborting execution.")
        sys.exit(1)
        
    with open(manifest_path, "r") as f:
        manifest = json.load(f)
        
    filename = os.path.basename(data_path)
    file_entry = manifest.get("files", {}).get(filename)
    
    if not file_entry:
        print(f"CRITICAL ERROR: File '{filename}' is not registered in manifest '{manifest_path}'.")
        print("P10-L4 Integrity check FAILED. Aborting execution.")
        sys.exit(1)
        
    expected_hash = file_entry.get("sha256")
    if actual_hash != expected_hash:
        print(f"CRITICAL ERROR: Hash mismatch for '{filename}'!")
        print(f"  Expected: {expected_hash}")
        print(f"  Actual:   {actual_hash}")
        print("P10-L4 Integrity check FAILED. Aborting execution.")
        sys.exit(1)
        
    print("Integrity check PASSED: SHA-256 matches manifest PIN.")
    return actual_hash

def stdlib_percentile(arr, p):
    if not arr:
        return 0.0
    s_arr = sorted(arr)
    k = (len(s_arr) - 1) * (p / 100.0)
    f = int(k)
    c = f + 1
    if c < len(s_arr):
        d0 = s_arr[f] * (c - k)
        d1 = s_arr[c] * (k - f)
        return float(d0 + d1)
    else:
        return float(s_arr[f])

def process_telemetry(raw_data):
    sp_map = {}
    for r in raw_data:
        key = (r['settlementDate'], r['settlementPeriod'])
        if key not in sp_map:
            sp_map[key] = {'E_PILLB-1': 0.0, 'E_PILLB-2': 0.0}
        sp_map[key][r['bmUnit']] = r['quantity']

    def build_window(filter_fn):
        rec_keys = [k for k in sorted(sp_map.keys()) if filter_fn(k[0])]
        dates = sorted(list(set(k[0] for k in rec_keys)))
        
        p1_chg, p1_dis = 0.0, 0.0
        p2_chg, p2_dis = 0.0, 0.0
        
        for k in rec_keys:
            q1 = sp_map[k]['E_PILLB-1']
            q2 = sp_map[k]['E_PILLB-2']
            if q1 < 0: p1_chg += abs(q1)
            else: p1_dis += q1
            if q2 < 0: p2_chg += abs(q2)
            else: p2_dis += q2

        tot_chg = p1_chg + p2_chg
        tot_dis = p1_dis + p2_dis
        rte = tot_dis / tot_chg
        
        max_exp = max((sp_map[k]['E_PILLB-1'] + sp_map[k]['E_PILLB-2']) * 2.0 for k in rec_keys)
        max_imp = max(abs(sp_map[k]['E_PILLB-1'] + sp_map[k]['E_PILLB-2']) * 2.0 for k in rec_keys if (sp_map[k]['E_PILLB-1'] + sp_map[k]['E_PILLB-2']) < 0)
        
        blocks = []
        cur = None
        block_count = 0
        for k in rec_keys:
            comb = sp_map[k]['E_PILLB-1'] + sp_map[k]['E_PILLB-2']
            if comb > 0:
                if cur is None:
                    cur = {'idx': block_count, 'start_k': k, 'end_k': k, 'energy': comb, 'sps': 1}
                    block_count += 1
                else:
                    cur['end_k'] = k
                    cur['energy'] += comb
                    cur['sps'] += 1
            else:
                if cur is not None:
                    blocks.append(cur)
                    cur = None
        if cur is not None:
            blocks.append(cur)
            
        top5 = sorted(blocks, key=lambda x: x['energy'], reverse=True)[:5]
        
        formatted_top5 = []
        for b in top5:
            formatted_top5.append({
                'block_index': b['idx'],
                'total_energy_mwh': round(b['energy'], 2),
                'duration_hours': b['sps'] * 0.5,
                'start': f"{b['start_k'][0]} SP{b['start_k'][1]}",
                'end': f"{b['end_k'][0]} SP{b['end_k'][1]}",
                'avg_power_mw': round(b['energy'] / (b['sps'] * 0.5), 2)
            })
            
        cf = (tot_dis / (len(dates) * 24.0 * 98.0)) * 100.0
        cycles = tot_dis / (len(dates) * 196.0)
        
        return {
            'num_days': len(dates),
            'total_charge_mwh': round(tot_chg, 2),
            'total_discharge_mwh': round(tot_dis, 2),
            'ac_ac_rte': round(rte, 4),
            'capacity_factor_pct': round(cf, 2),
            'daily_cycles': round(cycles, 3),
            'max_observed_combined_export_power_mw': round(max_exp, 2),
            'max_observed_combined_import_power_mw': round(max_imp, 2),
            'max_continuous_discharge_block': formatted_top5[0],
            'assets': {
                'E_PILLB-1': {
                    'total_charge_mwh': round(p1_chg, 2),
                    'total_discharge_mwh': round(p1_dis, 2),
                    'ac_ac_rte': round(p1_dis / p1_chg, 4)
                },
                'E_PILLB-2': {
                    'total_charge_mwh': round(p2_chg, 2),
                    'total_discharge_mwh': round(p2_dis, 2),
                    'ac_ac_rte': round(p2_dis / p2_chg, 4)
                }
            },
            'top_5_discharge_blocks': formatted_top5
        }

    m12 = {
        'audit_period': '12-Month (July 2025 - June 2026)',
        'unseen_11m_window': build_window(lambda d: d < '2026-06-01'),
        'scoped_1m_window': build_window(lambda d: d >= '2026-06-01'),
        'combined_12m_window': build_window(lambda d: True)
    }

    june_keys = [k for k in sorted(sp_map.keys()) if k[0] >= '2026-06-01']
    june_dates = sorted(list(set(k[0] for k in june_keys)))

    p1_chg, p1_dis, p1_rec = 0.0, 0.0, 0
    p2_chg, p2_dis, p2_rec = 0.0, 0.0, 0

    for r in raw_data:
        if r['settlementDate'] >= '2026-06-01':
            qty = r['quantity']
            if r['bmUnit'] == 'E_PILLB-1':
                p1_rec += 1
                if qty < 0: p1_chg += abs(qty)
                else: p1_dis += qty
            elif r['bmUnit'] == 'E_PILLB-2':
                p2_rec += 1
                if qty < 0: p2_chg += abs(qty)
                else: p2_dis += qty

    tot_chg = p1_chg + p2_chg
    tot_dis = p1_dis + p2_dis

    max_exp = max((sp_map[k]['E_PILLB-1'] + sp_map[k]['E_PILLB-2']) * 2.0 for k in june_keys)
    max_imp = max(abs(sp_map[k]['E_PILLB-1'] + sp_map[k]['E_PILLB-2']) * 2.0 for k in june_keys if (sp_map[k]['E_PILLB-1'] + sp_map[k]['E_PILLB-2']) < 0)

    june_top5 = m12['scoped_1m_window']['top_5_discharge_blocks']

    h_0_10, h_10_30, h_30_60, h_60_90, h_90plus = 0, 0, 0, 0, 0
    for k in june_keys:
        p_exp = (sp_map[k]['E_PILLB-1'] + sp_map[k]['E_PILLB-2']) * 2.0
        if p_exp >= 0:
            if p_exp < 10.0: h_0_10 += 1
            elif p_exp < 30.0: h_10_30 += 1
            elif p_exp < 60.0: h_30_60 += 1
            elif p_exp < 90.0: h_60_90 += 1
            else: h_90plus += 1

    tot_sp = len(june_keys)
    powers = [(sp_map[k]['E_PILLB-1'] + sp_map[k]['E_PILLB-2']) * 2.0 for k in june_keys]

    m_scoped = {
        'audit_period': 'June 2026',
        'assets': {
            'E_PILLB-1': {
                'name': 'Pillswood 1 Battery Storage',
                'capacity_mw': 49.9,
                'total_charge_mwh': round(p1_chg, 2),
                'total_discharge_mwh': round(p1_dis, 2),
                'ac_ac_rte': round(p1_dis / p1_chg, 4),
                'records_count': p1_rec
            },
            'E_PILLB-2': {
                'name': 'Pillswood 2 Battery Storage',
                'capacity_mw': 49.9,
                'total_charge_mwh': round(p2_chg, 2),
                'total_discharge_mwh': round(p2_dis, 2),
                'ac_ac_rte': round(p2_dis / p2_chg, 4),
                'records_count': p2_rec
            },
            'combined': {
                'capacity_mw': 99.8,
                'total_charge_mwh': round(tot_chg, 2),
                'total_discharge_mwh': round(tot_dis, 2),
                'ac_ac_rte': round(tot_dis / tot_chg, 4),
                'capacity_factor_pct': round((tot_dis / (len(june_dates) * 24.0 * 98.0)) * 100.0, 1),
                'daily_cycles': round(tot_dis / (len(june_dates) * 196.0), 3)
            }
        },
        'analytical_results': {
            'max_observed_combined_export_power_mw': round(max_exp, 2),
            'max_observed_combined_import_power_mw': round(max_imp, 2),
            'max_continuous_discharge_block': june_top5[0],
            'utilization_histogram': {
                'hours': {
                    '0-10_mw': h_0_10 * 0.5,
                    '10-30_mw': h_10_30 * 0.5,
                    '30-60_mw': h_30_60 * 0.5,
                    '60-90_mw': h_60_90 * 0.5,
                    '90+_mw': h_90plus * 0.5
                },
                'percentages': {
                    '0-10_mw': round((h_0_10 / tot_sp) * 100.0, 2),
                    '10-30_mw': round((h_10_30 / tot_sp) * 100.0, 2),
                    '30-60_mw': round((h_30_60 / tot_sp) * 100.0, 2),
                    '60-90_mw': round((h_60_90 / tot_sp) * 100.0, 2),
                    '90+_mw': round((h_90plus / tot_sp) * 100.0, 2)
                }
            },
            'dispatch_duration_curve_percentiles': {
                'max_100pct_mw': round(max_exp, 2),
                'p90_mw': round(stdlib_percentile(powers, 90), 2),
                'p75_mw': round(stdlib_percentile(powers, 75), 2),
                'p50_median_mw': round(stdlib_percentile(powers, 50), 2),
                'p25_mw': round(stdlib_percentile(powers, 25), 2),
                'p10_mw': round(stdlib_percentile(powers, 10), 2),
                'min_mw': round(min(powers), 1)
            },
            'top_5_discharge_blocks': june_top5
        }
    }

    return m12, m_scoped

def main():
    parser = argparse.ArgumentParser(description="Reproduce GB BESS Audit from frozen telemetry")
    parser.add_argument("--raw-data", type=str, default=None, help="Path to raw telemetry JSON file")
    parser.add_argument("--manifest", type=str, default=None, help="Path to data manifest JSON file")
    args = parser.parse_args()

    raw_path = args.raw_data or find_file("raw_pillswood_12m.json")
    manifest_path = args.manifest or find_file("data_manifest.json")

    actual_hash = verify_data_integrity(raw_path, manifest_path)

    print(f"\n--- Loading raw telemetry data from '{raw_path}' ---")
    with open(raw_path, "r") as f:
        raw_telemetry = json.load(f)
    print(f"Loaded {len(raw_telemetry)} telemetry records.")

    print(f"\n--- Regenerating Primary 12-Month Asset Metrics (metrics_12m.json) and Secondary Scoped Metrics (metrics.json) ---")
    m12, m_scoped = process_telemetry(raw_telemetry)

    out_12m_path = find_file("metrics_12m.json") or "metrics_12m.json"
    with open(out_12m_path, "w") as f:
        f.write(json.dumps(m12, indent=2))
    print(f"Regenerated '{os.path.basename(out_12m_path)}' (SHA-256: {calculate_sha256(out_12m_path)})")

    out_m_path = find_file("metrics.json") or "metrics.json"
    with open(out_m_path, "w") as f:
        f.write(json.dumps(m_scoped, indent=2))
    print(f"Regenerated '{os.path.basename(out_m_path)}' (SHA-256: {calculate_sha256(out_m_path)})")

    print("\n==================================================")
    print("P10 Offline Verification Pipeline Execution Complete!")
    print("Deterministically regenerated primary (metrics_12m.json) and secondary (metrics.json) metrics from raw telemetry.")
    print("==================================================")

if __name__ == "__main__":
    main()
