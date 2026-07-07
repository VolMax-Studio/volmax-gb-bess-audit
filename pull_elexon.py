#!/usr/bin/env python3
"""
pull_elexon.py
Acquires raw B1610 (Actual Generation Output Per Generation Unit) data 
from the Elexon Insights Solution API for a pre-filtered list of BESS BM units.
Saves the results to a frozen JSON archive.
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime, timedelta
import requests

def parse_args():
    parser = argparse.ArgumentParser(description="Acquire raw B1610 data from Elexon BMRS API")
    parser.add_argument(
        "--start", 
        type=str, 
        default="2026-06-01", 
        help="Start date of the audit window (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--end", 
        type=str, 
        default="2026-07-01", 
        help="End date of the audit window (YYYY-MM-DD, exclusive)"
    )
    parser.add_argument(
        "--output", 
        type=str, 
        default="data/raw_b1610_202606.json", 
        help="Path to save the frozen raw data JSON"
    )
    parser.add_argument(
        "--registry", 
        type=str, 
        default="bess_registry.json", 
        help="Path to the BESS registry JSON file"
    )
    parser.add_argument(
        "--chunk-size", 
        type=int, 
        default=40, 
        help="Number of BM units per API query to avoid URL length limits"
    )
    return parser.parse_args()

def get_date_range(start_str, end_str):
    start = datetime.strptime(start_str, "%Y-%m-%d")
    end = datetime.strptime(end_str, "%Y-%m-%d")
    current = start
    dates = []
    while current < end:
        dates.append(current)
        current += timedelta(days=1)
    return dates

def fetch_chunk_with_retry(url, params, headers, max_retries=3):
    for attempt in range(max_retries):
        try:
            r = requests.get(url, params=params, headers=headers, timeout=20)
            if r.status_code == 200:
                return r.json()
            elif r.status_code == 404:
                # Some days/chunks might return 404 if no data exists, log it and return empty
                print(f"  Warning: Received 404 for chunk. Returning empty list.")
                return []
            else:
                print(f"  Warning: Attempt {attempt+1} failed with status code {r.status_code}: {r.text[:200]}")
        except Exception as e:
            print(f"  Warning: Attempt {attempt+1} failed with exception: {e}")
        
        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)  # Exponential backoff
            
    raise RuntimeError(f"Failed to fetch data after {max_retries} attempts.")

def main():
    args = parse_args()
    
    # Verify registry file exists
    if not os.path.exists(args.registry):
        print(f"Error: Registry file '{args.registry}' not found.")
        sys.exit(1)
        
    # Load registry and extract BM Unit IDs
    with open(args.registry, "r") as f:
        registry = json.load(f)
        
    bm_units = [u["elexonBmUnit"] for u in registry if u.get("elexonBmUnit")]
    print(f"Loaded {len(bm_units)} BESS BM units from '{args.registry}'")
    
    # Base URL for Elexon B1610 stream
    url = "https://data.elexon.co.uk/bmrs/api/v1/datasets/B1610/stream"
    headers = {
        "User-Agent": "VolMax BESS Auditor (contact@volmax-studio.com)",
        "Accept": "application/json"
    }
    
    # Get date range
    dates = get_date_range(args.start, args.end)
    print(f"Acquiring data from {args.start} to {args.end} ({len(dates)} days)")
    
    # Split BM units into chunks
    chunk_size = args.chunk_size
    bm_chunks = [bm_units[i:i + chunk_size] for i in range(0, len(bm_units), chunk_size)]
    print(f"Split {len(bm_units)} BM units into {len(bm_chunks)} chunks of size <= {chunk_size}")
    
    all_records = []
    total_queries = len(dates) * len(bm_chunks)
    query_count = 0
    
    # Ensure output directory exists
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        
    start_time = time.time()
    
    for dt in dates:
        date_str = dt.strftime("%Y-%m-%d")
        # Define start/end times in UTC
        from_str = f"{date_str}T00:00:00Z"
        to_str = f"{date_str}T23:59:59Z"
        
        print(f"Processing date: {date_str}")
        
        for idx, chunk in enumerate(bm_chunks):
            query_count += 1
            print(f"  [{query_count}/{total_queries}] Querying chunk {idx+1}/{len(bm_chunks)} ({len(chunk)} units)...")
            
            params = {
                "from": from_str,
                "to": to_str,
                "bmUnit": chunk
            }
            
            try:
                records = fetch_chunk_with_retry(url, params, headers)
                all_records.extend(records)
                print(f"    Success: Fetched {len(records)} records.")
            except Exception as e:
                print(f"    Error: {e}")
                print("    Aborting data acquisition to maintain data integrity.")
                sys.exit(1)
                
            # Respectful rate limiting
            time.sleep(0.5)
            
    elapsed_time = time.time() - start_time
    print(f"\nData acquisition complete in {elapsed_time:.1f} seconds.")
    print(f"Total records fetched: {len(all_records)}")
    
    # Write to local frozen file
    print(f"Saving frozen raw data to '{args.output}'...")
    with open(args.output, "w") as f:
        json.dump(all_records, f, indent=2)
        
    print("Done!")

if __name__ == "__main__":
    main()
