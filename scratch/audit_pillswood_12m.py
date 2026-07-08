import json
import os
from datetime import datetime

raw_data_path = "/home/volmax-studio/volmax-projects/iot2/PORTFOLIO/volmax-gb-bess-audit/audits/UK-HARMONY-001/raw_pillswood_12m.json"
output_metrics_path = "/home/volmax-studio/volmax-projects/iot2/PORTFOLIO/volmax-gb-bess-audit/audits/UK-HARMONY-001/metrics_12m.json"

# Ensure output directory exists
os.makedirs(os.path.dirname(output_metrics_path), exist_ok=True)

print("Loading raw data...")
with open(raw_data_path, "r") as f:
    telemetry = json.load(f)

# Sort chronologically
pillswood_1 = []
pillswood_2 = []

for r in telemetry:
    bmu = r.get("bmUnit")
    if bmu == "E_PILLB-1":
        pillswood_1.append(r)
    elif bmu == "E_PILLB-2":
        pillswood_2.append(r)

def sort_key(r):
    # settlementDate is YYYY-MM-DD
    return (r["settlementDate"], r["settlementPeriod"])

pillswood_1.sort(key=sort_key)
pillswood_2.sort(key=sort_key)

# Align into periods map
periods_map = {}
for r in pillswood_1:
    k = (r["settlementDate"], r["settlementPeriod"])
    periods_map[k] = {"E_PILLB-1": r["quantity"], "E_PILLB-2": 0.0}

for r in pillswood_2:
    k = (r["settlementDate"], r["settlementPeriod"])
    if k not in periods_map:
        periods_map[k] = {"E_PILLB-1": 0.0, "E_PILLB-2": r["quantity"]}
    else:
        periods_map[k]["E_PILLB-2"] = r["quantity"]

sorted_periods = sorted(periods_map.keys())

# Define windows
# unseen_11m: July 1, 2025 to May 31, 2026 (date < 2026-06-01)
# scoped_1m: June 1, 2026 to June 30, 2026 (date >= 2026-06-01)
# combined_12m: all

def calculate_metrics_for_window(periods_list):
    p1_charge = 0.0
    p1_discharge = 0.0
    p2_charge = 0.0
    p2_discharge = 0.0
    
    combined_timeline = []
    unique_dates = set()
    
    for k in periods_list:
        unique_dates.add(k[0])
        q1 = periods_map[k]["E_PILLB-1"]
        q2 = periods_map[k]["E_PILLB-2"]
        
        if q1 < 0:
            p1_charge += abs(q1)
        else:
            p1_discharge += q1
            
        if q2 < 0:
            p2_charge += abs(q2)
        else:
            p2_discharge += q2
            
        q_comb = q1 + q2
        combined_timeline.append({
            "date": k[0],
            "period": k[1],
            "q1": q1,
            "q2": q2,
            "q_comb": q_comb,
            "p_comb": q_comb * 2.0  # power in MW
        })
        
    num_days = len(unique_dates) if unique_dates else 1
    
    export_powers = [item["p_comb"] for item in combined_timeline if item["q_comb"] > 0]
    import_powers = [abs(item["p_comb"]) for item in combined_timeline if item["q_comb"] < 0]
    
    max_p_export = max(export_powers) if export_powers else 0.0
    max_p_import = max(import_powers) if import_powers else 0.0
    
    # Capacity Factor
    # Claim capacity: 98 MW
    cf_denom_mwh = 98.0 * 24.0 * num_days
    cf_pct = (p1_discharge + p2_discharge) / cf_denom_mwh * 100.0 if cf_denom_mwh > 0 else 0.0
    
    # Daily Cycling
    # Claim capacity: 196 MWh
    daily_cycles = ((p1_discharge + p2_discharge) / 196.0) / num_days if num_days > 0 else 0.0
    
    # Find continuous discharge blocks
    continuous_blocks = []
    current_block = []
    
    for item in combined_timeline:
        if item["q_comb"] > 0:
            current_block.append(item)
        else:
            if current_block:
                continuous_blocks.append(current_block)
                current_block = []
    if current_block:
        continuous_blocks.append(current_block)
        
    block_metrics = []
    for i, block in enumerate(continuous_blocks):
        energy = sum([item["q_comb"] for item in block])
        duration_hours = len(block) * 0.5
        start_date = block[0]["date"]
        start_period = block[0]["period"]
        end_date = block[-1]["date"]
        end_period = block[-1]["period"]
        avg_power = energy / duration_hours if duration_hours > 0 else 0.0
        block_metrics.append({
            "block_index": i,
            "total_energy_mwh": round(energy, 2),
            "duration_hours": duration_hours,
            "start": f"{start_date} SP{start_period}",
            "end": f"{end_date} SP{end_period}",
            "avg_power_mw": round(avg_power, 2)
        })
        
    block_metrics.sort(key=lambda x: x["total_energy_mwh"], reverse=True)
    top_block = block_metrics[0] if block_metrics else None
    
    p1_rte = p1_discharge / p1_charge if p1_charge > 0 else 0.0
    p2_rte = p2_discharge / p2_charge if p2_charge > 0 else 0.0
    comb_charge = p1_charge + p2_charge
    comb_discharge = p1_discharge + p2_discharge
    comb_rte = comb_discharge / comb_charge if comb_charge > 0 else 0.0
    
    return {
        "num_days": num_days,
        "total_charge_mwh": round(comb_charge, 2),
        "total_discharge_mwh": round(comb_discharge, 2),
        "ac_ac_rte": round(comb_rte, 4),
        "capacity_factor_pct": round(cf_pct, 2),
        "daily_cycles": round(daily_cycles, 3),
        "max_observed_combined_export_power_mw": round(max_p_export, 2),
        "max_observed_combined_import_power_mw": round(max_p_import, 2),
        "max_continuous_discharge_block": top_block,
        "assets": {
            "E_PILLB-1": {
                "total_charge_mwh": round(p1_charge, 2),
                "total_discharge_mwh": round(p1_discharge, 2),
                "ac_ac_rte": round(p1_rte, 4)
            },
            "E_PILLB-2": {
                "total_charge_mwh": round(p2_charge, 2),
                "total_discharge_mwh": round(p2_discharge, 2),
                "ac_ac_rte": round(p2_rte, 4)
            }
        },
        "top_5_discharge_blocks": block_metrics[:5]
    }

# Filter keys
unseen_keys = [k for k in sorted_periods if k[0] < "2026-06-01"]
scoped_keys = [k for k in sorted_periods if "2026-06-01" <= k[0] <= "2026-06-30"]
combined_keys = sorted_periods

print(f"Total periods: {len(sorted_periods)}")
print(f"Unseen periods: {len(unseen_keys)}")
print(f"Scoped periods: {len(scoped_keys)}")

metrics_unseen = calculate_metrics_for_window(unseen_keys)
metrics_scoped = calculate_metrics_for_window(scoped_keys)
metrics_combined = calculate_metrics_for_window(combined_keys)

output_data = {
    "audit_period": "12-Month (July 2025 - June 2026)",
    "unseen_11m_window": metrics_unseen,
    "scoped_1m_window": metrics_scoped,
    "combined_12m_window": metrics_combined
}

with open(output_metrics_path, "w") as f:
    json.dump(output_data, f, indent=2)

print("12-Month analysis complete! Results written to:", output_metrics_path)
print("\n--- COMBINED 12-MONTH SUMMARY ---")
print(f"Days: {metrics_combined['num_days']}")
print(f"Charge (MWh): {metrics_combined['total_charge_mwh']}")
print(f"Discharge (MWh): {metrics_combined['total_discharge_mwh']}")
print(f"RTE: {metrics_combined['ac_ac_rte']:.4f}")
print(f"CF: {metrics_combined['capacity_factor_pct']}%")
print(f"Daily Cycles: {metrics_combined['daily_cycles']:.3f}")
print(f"Max Export Power (MW): {metrics_combined['max_observed_combined_export_power_mw']}")
print(f"Max Continuous Discharge Block (MWh): {metrics_combined['max_continuous_discharge_block']['total_energy_mwh'] if metrics_combined['max_continuous_discharge_block'] else 0.0}")
