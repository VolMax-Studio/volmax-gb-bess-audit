import json
import os

raw_data_path = "/home/volmax-studio/volmax-projects/iot2/PORTFOLIO/volmax-gb-bess-audit/data/raw_b1610_202606.json"
output_metrics_path = "/home/volmax-studio/volmax-projects/iot2/PORTFOLIO/volmax-gb-bess-audit/audits/UK-HARMONY-001/metrics.json"

# Ensure output directory exists
os.makedirs(os.path.dirname(output_metrics_path), exist_ok=True)

with open(raw_data_path, "r") as f:
    telemetry = json.load(f)

# Group telemetry by BM Unit and sort chronologically
pillswood_1 = []
pillswood_2 = []

for r in telemetry:
    bmu = r.get("bmUnit")
    if bmu == "E_PILLB-1":
        pillswood_1.append(r)
    elif bmu == "E_PILLB-2":
        pillswood_2.append(r)

def sort_key(r):
    return (r["settlementDate"], r["settlementPeriod"])

pillswood_1.sort(key=sort_key)
pillswood_2.sort(key=sort_key)

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

p1_charge = 0.0
p1_discharge = 0.0
p2_charge = 0.0
p2_discharge = 0.0

combined_timeline = []

for k in sorted_periods:
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
        "p_comb": q_comb * 2.0 # power in MW
    })

# Find maximum combined export/import power (MW)
export_powers = [item["p_comb"] for item in combined_timeline if item["q_comb"] > 0]
import_powers = [abs(item["p_comb"]) for item in combined_timeline if item["q_comb"] < 0]

max_p_export = max(export_powers) if export_powers else 0.0
max_p_import = max(import_powers) if import_powers else 0.0

# 1. Capacity Factor (CF) for the month (June has 30 days)
# Claim capacity: 98 MW
num_days = 30
cf_denom_mwh = 98.0 * 24.0 * num_days
cf_pct = (p1_discharge + p2_discharge) / cf_denom_mwh * 100.0

# 2. Daily Cycling
# Claim capacity: 196 MWh
daily_cycles = ((p1_discharge + p2_discharge) / 196.0) / num_days

# 3. Utilization Histogram (counting settlement periods when combined power > 0)
hist_0_10 = 0
hist_10_30 = 0
hist_30_60 = 0
hist_60_90 = 0
hist_90_plus = 0

for p_val in export_powers:
    if 0.0 < p_val <= 10.0:
        hist_0_10 += 1
    elif 10.0 < p_val <= 30.0:
        hist_10_30 += 1
    elif 30.0 < p_val <= 60.0:
        hist_30_60 += 1
    elif 60.0 < p_val <= 90.0:
        hist_60_90 += 1
    elif p_val > 90.0:
        hist_90_plus += 1

total_export_periods = len(export_powers)

# Convert period counts to hours (each period is 0.5 hours)
hist_hours = {
    "0-10_mw": round(hist_0_10 * 0.5, 1),
    "10-30_mw": round(hist_10_30 * 0.5, 1),
    "30-60_mw": round(hist_30_60 * 0.5, 1),
    "60-90_mw": round(hist_60_90 * 0.5, 1),
    "90+_mw": round(hist_90_plus * 0.5, 1)
}

hist_percentages = {
    "0-10_mw": round(hist_0_10 / total_export_periods * 100.0, 2) if total_export_periods > 0 else 0.0,
    "10-30_mw": round(hist_10_30 / total_export_periods * 100.0, 2) if total_export_periods > 0 else 0.0,
    "30-60_mw": round(hist_30_60 / total_export_periods * 100.0, 2) if total_export_periods > 0 else 0.0,
    "60-90_mw": round(hist_60_90 / total_export_periods * 100.0, 2) if total_export_periods > 0 else 0.0,
    "90+_mw": round(hist_90_plus / total_export_periods * 100.0, 2) if total_export_periods > 0 else 0.0
}

# 4. Dispatch Duration Curve metrics (percentiles of export power)
sorted_exports = sorted(export_powers, reverse=True)
def get_percentile(lst, p):
    if not lst:
        return 0.0
    idx = int(len(lst) * p)
    idx = min(idx, len(lst) - 1)
    return lst[idx]

dispatch_duration_percentiles = {
    "max_100pct_mw": round(sorted_exports[0], 2) if sorted_exports else 0.0,
    "p90_mw": round(get_percentile(sorted_exports, 0.1), 2),
    "p75_mw": round(get_percentile(sorted_exports, 0.25), 2),
    "p50_median_mw": round(get_percentile(sorted_exports, 0.5), 2),
    "p25_mw": round(get_percentile(sorted_exports, 0.75), 2),
    "p10_mw": round(get_percentile(sorted_exports, 0.9), 2),
    "min_mw": round(sorted_exports[-1], 2) if sorted_exports else 0.0
}

# Find maximum continuous discharge blocks
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

# Prepare final metrics JSON
p1_rte = p1_discharge / p1_charge if p1_charge > 0 else 0.0
p2_rte = p2_discharge / p2_charge if p2_charge > 0 else 0.0
comb_charge = p1_charge + p2_charge
comb_discharge = p1_discharge + p2_discharge
comb_rte = comb_discharge / comb_charge if comb_charge > 0 else 0.0

metrics_output = {
    "audit_period": "June 2026",
    "assets": {
        "E_PILLB-1": {
            "name": "Pillswood 1 Battery Storage",
            "capacity_mw": 49.9,
            "total_charge_mwh": round(p1_charge, 2),
            "total_discharge_mwh": round(p1_discharge, 2),
            "ac_ac_rte": round(p1_rte, 4),
            "records_count": len(pillswood_1)
        },
        "E_PILLB-2": {
            "name": "Pillswood 2 Battery Storage",
            "capacity_mw": 49.9,
            "total_charge_mwh": round(p2_charge, 2),
            "total_discharge_mwh": round(p2_discharge, 2),
            "ac_ac_rte": round(p2_rte, 4),
            "records_count": len(pillswood_2)
        },
        "combined": {
            "capacity_mw": 99.8,
            "total_charge_mwh": round(comb_charge, 2),
            "total_discharge_mwh": round(comb_discharge, 2),
            "ac_ac_rte": round(comb_rte, 4),
            "capacity_factor_pct": round(cf_pct, 2),
            "daily_cycles": round(daily_cycles, 3)
        }
    },
    "analytical_results": {
        "max_observed_combined_export_power_mw": round(max_p_export, 2),
        "max_observed_combined_import_power_mw": round(max_p_import, 2),
        "max_continuous_discharge_block": top_block,
        "utilization_histogram": {
            "hours": hist_hours,
            "percentages": hist_percentages
        },
        "dispatch_duration_curve_percentiles": dispatch_duration_percentiles,
        "top_5_discharge_blocks": block_metrics[:5]
    }
}

with open(output_metrics_path, "w") as f:
    json.dump(metrics_output, f, indent=2)

print("Analysis complete! Results:")
print(json.dumps(metrics_output, indent=2))
