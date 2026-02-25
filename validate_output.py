#!/usr/bin/env python3
"""
validate_output.py — Spot-check computed percentiles against DQYDJ published values.

DQYDJ publishes percentile tables derived from the same IPUMS-CPS source data.
This script compares your computed output to their published 2025 figures to
verify your pipeline is working correctly.

Exact matches are not expected due to:
  - Possible differences in worker screen definition
  - Rounding approaches
  - Potential differences in IPUMS version/extract timing
  - Interpolation method variations

But values should be within ~5% for most cells. Larger deviations at p99 are
normal due to top-coding and small sample sizes.

Usage:
    python validate_output.py income_percentiles.json
"""

import json
import sys

# Known DQYDJ 2025 values (income year 2024) — from their published tables
# Source: https://dqydj.com/income-percentile-by-age-calculator/
DQYDJ_2025 = {
    25: {'p25':24013, 'p50':41150, 'p75':65000, 'p90':94040, 'p99':194750},
    29: {'p25':34150, 'p50':55000, 'p75':85400, 'p90':137020, 'p99':396501},
    30: {'p25':32500, 'p50':52002, 'p75':84017, 'p90':130030, 'p99':324648},
    35: {'p25':33520, 'p50':60000, 'p75':100000, 'p90':167000, 'p99':460011},
    40: {'p25':39000, 'p50':61970, 'p75':106020, 'p90':178001, 'p99':483400},
    45: {'p25':37440, 'p50':67144, 'p75':117001, 'p90':190100, 'p99':600003},
    50: {'p25':36931, 'p50':65000, 'p75':113501, 'p90':190900, 'p99':554105},
    55: {'p25':36680, 'p50':63350, 'p75':110000, 'p90':170000, 'p99':528575},
    60: {'p25':36000, 'p50':62001, 'p75':101700, 'p90':170060, 'p99':585000},
    65: {'p25':40041, 'p50':70001, 'p75':114850, 'p90':201805, 'p99':611820},
}


def validate(filepath):
    with open(filepath) as f:
        data = json.load(f)

    # Find income year 2024 (which is what DQYDJ 2025 edition covers)
    if '2024' not in data['data']:
        print("WARNING: Income year 2024 not found in output.")
        print(f"  Available years: {sorted(data['data'].keys())}")
        # Try the latest year
        latest = sorted(data['data'].keys())[-1]
        print(f"  Comparing against latest year: {latest}")
        year_data = data['data'][latest]
    else:
        year_data = data['data']['2024']

    print(f"{'Age':>4} {'Perc':>5} {'Computed':>12} {'DQYDJ':>12} {'Diff%':>8} {'Status':>8}")
    print(f"{'-'*4} {'-'*5} {'-'*12} {'-'*12} {'-'*8} {'-'*8}")

    total = 0
    within_5 = 0
    within_10 = 0

    for age in sorted(DQYDJ_2025.keys()):
        age_str = str(age)
        if age_str not in year_data:
            print(f"{age:>4}   — not in computed data")
            continue

        computed = year_data[age_str]

        for pkey, dqydj_val in sorted(DQYDJ_2025[age].items()):
            total += 1
            comp_val = computed.get(pkey)

            if comp_val is None:
                print(f"{age:>4} {pkey:>5} {'MISSING':>12} {dqydj_val:>12,} {'—':>8} {'MISS':>8}")
                continue

            diff_pct = abs(comp_val - dqydj_val) / dqydj_val * 100

            if diff_pct <= 5:
                status = "  OK"
                within_5 += 1
                within_10 += 1
            elif diff_pct <= 10:
                status = "  ~OK"
                within_10 += 1
            else:
                status = " CHECK"

            print(f"{age:>4} {pkey:>5} ${comp_val:>11,.0f} ${dqydj_val:>11,} {diff_pct:>7.1f}% {status:>8}")

    print(f"\n{'='*60}")
    print(f"Results: {within_5}/{total} within 5%, {within_10}/{total} within 10%")

    if within_5 / total >= 0.8:
        print("✓ Pipeline appears to be working correctly.")
    elif within_10 / total >= 0.7:
        print("~ Pipeline is approximately correct but check worker screen.")
    else:
        print("✗ Significant deviations — check data extract and filters.")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python validate_output.py income_percentiles.json")
        sys.exit(1)
    validate(sys.argv[1])
