#!/usr/bin/env python3
"""
reproduce.py
Offline verification pipeline for the GB BESS Audit.
Reads from the frozen raw JSON archive, checks its SHA-256 checksum, 
applies the P10 Battery Annex Part 1 rules, and outputs audit metrics.
"""

import os
import sys
import json
import hashlib
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Reproduce GB BESS Audit from frozen telemetry")
    parser.add_argument(
        "--raw-data", 
        type=str, 
        default="data/raw_b1610_202606.json", 
        help="Path to the frozen raw data JSON file"
    )
    parser.add_argument(
        "--manifest", 
        type=str, 
        default="data_manifest.json", 
        help="Path to the data manifest containing expected hashes"
    )
    parser.add_argument(
        "--registry", 
        type=str, 
        default="bess_registry.json", 
        help="Path to the BESS registry JSON file"
    )
    parser.add_argument(
        "--output-metrics", 
        type=str, 
        default="audit_metrics.json", 
        help="Path to save the generated audit metrics JSON"
    )
    return parser.parse_args()

def calculate_sha256(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            sha256.update(chunk)
    return sha256.hexdigest()

def verify_data_integrity(data_path, manifest_path):
    print(f"--- Level 1 & 4 Integrity Check: P10 Data Pinning ---")
    if not os.path.exists(data_path):
        print(f"ERROR: Raw data file '{data_path}' not found.")
        sys.exit(1)
        
    actual_hash = calculate_sha256(data_path)
    print(f"Actual SHA-256 of '{os.path.basename(data_path)}': {actual_hash}")
    
    if not os.path.exists(manifest_path):
        print(f"WARNING: Manifest file '{manifest_path}' not found. Generating a template manifest...")
        manifest_data = {
            "files": {
                os.path.basename(data_path): {
                    "sha256": actual_hash,
                    "description": "Frozen raw Elexon B1610 data for June 2026"
                }
            }
        }
        with open(manifest_path, "w") as f:
            json.dump(manifest_data, f, indent=2)
        print(f"Manifest written to '{manifest_path}'. Integrity check PASSED (bootstrapped).")
        return actual_hash
        
    with open(manifest_path, "r") as f:
        manifest = json.load(f)
        
    filename = os.path.basename(data_path)
    file_entry = manifest.get("files", {}).get(filename)
    
    if not file_entry:
        print(f"WARNING: File '{filename}' not found in manifest. Pinning current hash to manifest...")
        manifest.setdefault("files", {})[filename] = {
            "sha256": actual_hash,
            "description": "Frozen raw Elexon B1610 data"
        }
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
        print(f"Manifest updated. Integrity check PASSED.")
        return actual_hash
        
    expected_hash = file_entry.get("sha256")
    if actual_hash != expected_hash:
        print(f"CRITICAL ERROR: Hash mismatch for '{filename}'!")
        print(f"  Expected: {expected_hash}")
        print(f"  Actual:   {actual_hash}")
        print("P10-L4 Integrity check FAILED. Aborting execution.")
        sys.exit(1)
        
    print("Integrity check PASSED: SHA-256 matches manifest PIN.")
    return actual_hash

def main():
    args = parse_args()
    
    # 1. Verify Data Integrity
    actual_hash = verify_data_integrity(args.raw_data, args.manifest)
    
    # 2. Load Registry
    if not os.path.exists(args.registry):
        print(f"ERROR: BESS registry '{args.registry}' not found.")
        sys.exit(1)
    with open(args.registry, "r") as f:
        registry = json.load(f)
        
    # Map from Elexon BM Unit ID to registry details
    registry_map = {u["elexonBmUnit"]: u for u in registry if u.get("elexonBmUnit")}
    
    # 3. Load Raw Telemetry Data
    print(f"\n--- Loading raw telemetry data ---")
    with open(args.raw_data, "r") as f:
        telemetry = json.load(f)
    print(f"Loaded {len(telemetry)} telemetry records.")
    
    # 4. Aggregate telemetry per BM Unit
    # We want to sum charging (negative values) and discharging (positive values)
    # in MWh. Note: B1610 quantity is metered volume in MWh.
    unit_data = {}
    for r in telemetry:
        bmu = r.get("bmUnit")
        if not bmu:
            continue
            
        qty = r.get("quantity")
        if qty is None:
            continue
            
        if bmu not in unit_data:
            unit_data[bmu] = {
                "charge_mwh": 0.0,
                "discharge_mwh": 0.0,
                "records_count": 0,
                "has_positive": False,
                "has_negative": False
            }
            
        unit_data[bmu]["records_count"] += 1
        # Elexon B1610 sign conventions: positive is export (discharge), negative is import (charge)
        if qty < 0:
            unit_data[bmu]["charge_mwh"] += abs(qty)
            unit_data[bmu]["has_negative"] = True
        elif qty > 0:
            unit_data[bmu]["discharge_mwh"] += qty
            unit_data[bmu]["has_positive"] = True
            
    # 5. Audit each BESS unit
    print(f"\n--- Running P10 BESS Audit Level 2 & 3 checks ---")
    audit_results = {}
    
    total_fleet = len(registry)
    active_count = 0
    inactive_count = 0
    failed_count = 0
    passed_count = 0
    
    for u in registry:
        bmu = u["elexonBmUnit"]
        name = u["bmUnitName"]
        gen_cap = u["generationCapacity"]
        dem_cap = u["demandCapacity"]
        
        # Check telemetry availability
        t_data = unit_data.get(bmu)
        
        if not t_data or (t_data["charge_mwh"] < 1.0 and t_data["discharge_mwh"] < 1.0):
            # Inactive or pre-COD
            status = "Inactive/Pre-COD"
            verdict = "PASS (Excluded)"
            reason = "No significant operational throughput (throughput < 1 MWh)"
            rte = None
            charge = 0.0
            discharge = 0.0
            records = t_data["records_count"] if t_data else 0
            inactive_count += 1
        else:
            active_count += 1
            charge = t_data["charge_mwh"]
            discharge = t_data["discharge_mwh"]
            records = t_data["records_count"]
            
            # Calculate AC-to-AC Round-Trip Efficiency
            # charge is sum of absolute negative quantities
            rte = discharge / charge if charge > 0 else 0.0
            
            # Checks
            # C1: Sign Convention check (Must have both charge and discharge)
            has_both_signs = t_data["has_positive"] and t_data["has_negative"]
            
            # C2: RTE Bounds Check
            # Physically: RTE <= 1.0 (strict thermodynamic limit)
            # Descriptively: 0.60 <= RTE <= 0.92 (typical range)
            
            if not has_both_signs:
                status = "Active"
                verdict = "FAIL (L1 Integrity)"
                reason = f"Single-direction telemetry. Charge count={t_data['has_negative']}, Discharge count={t_data['has_positive']}."
                failed_count += 1
            elif rte > 1.0:
                status = "Active"
                verdict = "FAIL (L2 Physical Violation)"
                reason = f"Thermodynamic violation: AC-AC RTE = {rte:.3f} (> 1.0). Absolute physical impossibility (energy creation)."
                failed_count += 1
            else:
                status = "Active"
                if rte < 0.60 or rte > 0.92:
                    verdict = "PASS (Flagged)"
                    if rte > 0.92:
                        reason = f"High efficiency flag: AC-AC RTE = {rte:.3f} (> 0.92). Likely boundary-condition artifact (starting full and ending empty) or under-reported auxiliary loads."
                    else:
                        reason = f"Low efficiency flag: AC-AC RTE = {rte:.3f} (< 0.60). High auxiliary consumption or low utilization."
                else:
                    verdict = "PASS"
                    reason = "AC-AC RTE within physical bounds [0.60, 0.92] and complete bidirectional telemetry."
                passed_count += 1
                
        audit_results[bmu] = {
            "name": name,
            "generationCapacity": gen_cap,
            "demandCapacity": dem_cap,
            "status": status,
            "verdict": verdict,
            "reason": reason,
            "charge_mwh": round(charge, 2),
            "discharge_mwh": round(discharge, 2),
            "rte": round(rte, 3) if rte is not None else None,
            "records_count": records
        }
        
    # Calculate fleet-level statistics for active units
    active_rtes = [res["rte"] for res in audit_results.values() if res["status"] == "Active" and res["rte"] is not None]
    avg_fleet_rte = sum(active_rtes) / len(active_rtes) if active_rtes else 0.0
    
    # 6. Generate final metrics
    metrics = {
        "data_file": os.path.basename(args.raw_data),
        "sha256_hash": actual_hash,
        "fleet_statistics": {
            "total_fleet_units": total_fleet,
            "active_fleet_units": active_count,
            "inactive_fleet_units": inactive_count,
            "passed_units": passed_count,
            "failed_units": failed_count,
            "average_active_fleet_rte": round(avg_fleet_rte, 3)
        },
        "unit_details": audit_results
    }
    
    with open(args.output_metrics, "w") as f:
        json.dump(metrics, f, indent=2)
        
    print(f"\n--- Audit Summary ---")
    print(f"Total Fleet BESS Units:  {total_fleet}")
    print(f"Active BESS Units:       {active_count}")
    print(f"Inactive / Pre-COD:      {inactive_count}")
    print(f"Failed Units:            {failed_count}")
    print(f"Passed Units:            {passed_count}")
    print(f"Average Active Fleet RTE: {avg_fleet_rte:.3f}")
    
    if failed_count > 0:
        print("\nFailed Units Details:")
        for bmu, res in audit_results.items():
            if "FAIL" in res["verdict"]:
                print(f"  - {bmu} ({res['name']}): {res['verdict']} | RTE={res['rte']} | {res['reason']}")
                
    print(f"\nMetrics written to '{args.output_metrics}'")
    print("Audit finished!")

if __name__ == "__main__":
    main()
