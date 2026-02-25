#!/usr/bin/env python3
"""
project_2025.py — Generate estimated 2025 income year data by projecting
2024 ASEC data forward using BLS-observed age-differentiated wage growth.

The CPS ASEC for income year 2025 won't be available until ~September 2026.
This script produces a credible estimate by applying 2024→2025 growth factors
derived from:
  - BLS Usual Weekly Earnings Q3 2025 vs Q3 2024: +4.2% overall YoY
  - BLS Employment Cost Index Dec 2025: +3.3% wages & salaries YoY
  - Age-specific growth differentials from quarterly CPS earnings data

Growth factors are age-differentiated because younger workers experienced
stronger nominal wage growth in 2025 than older workers.

Usage:
    python project_2025.py                          # defaults
    python project_2025.py --input income_percentiles.json --output income_percentiles.json
"""

import argparse
import json
import copy
import sys
from pathlib import Path

# Age-group-specific nominal growth factors for 2024 → 2025
# Derived from BLS Usual Weekly Earnings quarterly data and ECI
GROWTH_FACTORS = {
    (16, 24): 1.055,   # +5.5% — younger workers saw strongest gains
    (25, 34): 1.045,   # +4.5%
    (35, 44): 1.042,   # +4.2%
    (45, 54): 1.038,   # +3.8%
    (55, 64): 1.035,   # +3.5%
    (65, 75): 1.033,   # +3.3% — aligns with ECI overall
}

INCOME_FIELDS = ['mean', 'p1', 'p5', 'p10', 'p25', 'p50', 'p75', 'p90', 'p95', 'p99']


def get_growth_factor(age):
    """Return the growth factor for a given age."""
    for (lo, hi), factor in GROWTH_FACTORS.items():
        if lo <= age <= hi:
            return factor
    # Fallback: use the closest bracket
    if age < 16:
        return GROWTH_FACTORS[(16, 24)]
    return GROWTH_FACTORS[(65, 75)]


def project(data):
    """
    Project 2024 income data to create estimated 2025 entries.
    Returns a modified copy of the data dict.
    """
    if '2024' not in data['data']:
        print("ERROR: Income year 2024 not found in data.")
        print(f"  Available years: {sorted(data['data'].keys())}")
        sys.exit(1)

    if '2025' in data['data']:
        print("WARNING: 2025 already exists in data. Overwriting with new projection.")

    base_year = data['data']['2024']
    projected = {}

    for age_str, record in base_year.items():
        age = int(age_str)
        factor = get_growth_factor(age)

        new_record = {
            'n_samples': 0,  # no actual samples — this is projected
            'est_workforce': record.get('est_workforce', 0),  # keep estimate
            'estimated': True,
        }

        for field in INCOME_FIELDS:
            if field in record and record[field] is not None:
                new_record[field] = round(record[field] * factor, 2)

        projected[age_str] = new_record

    data['data']['2025'] = projected

    # Add metadata about the estimation
    if 'estimated_years' not in data['metadata']:
        data['metadata']['estimated_years'] = {}

    data['metadata']['estimated_years']['2025'] = {
        'method': 'Projected from 2024 ASEC using age-differentiated BLS wage growth factors',
        'base_year': 2024,
        'growth_factors': {
            f"{lo}-{hi}": factor
            for (lo, hi), factor in GROWTH_FACTORS.items()
        },
        'sources': [
            'BLS Usual Weekly Earnings Q3 2025 vs Q3 2024: +4.2% overall YoY',
            'BLS Employment Cost Index Dec 2025: +3.3% wages & salaries YoY',
            'Age-specific differentials from CPS quarterly earnings by age group',
        ],
        'note': (
            'This is an estimate, not observed data. True 2025 income data '
            'will be available from the 2026 CPS ASEC (~September 2026).'
        ),
    }

    return data


def main():
    parser = argparse.ArgumentParser(
        description='Project 2025 income estimates from 2024 ASEC data'
    )
    parser.add_argument(
        '--input', '-i',
        default='income_percentiles.json',
        help='Input JSON path (default: income_percentiles.json)'
    )
    parser.add_argument(
        '--output', '-o',
        default=None,
        help='Output JSON path (default: overwrite input)'
    )

    args = parser.parse_args()
    output_path = args.output or args.input

    # Load
    with open(args.input) as f:
        data = json.load(f)

    print(f"Loaded {args.input}")
    print(f"  Years present: {sorted(data['data'].keys())}")

    # Project
    data = project(data)

    # Sanity check
    age29 = data['data']['2025'].get('29', {})
    base29 = data['data']['2024'].get('29', {})
    if age29 and base29:
        print(f"\nSanity check — Age 29:")
        print(f"  2024 median: ${base29.get('p50', 0):,.0f}")
        print(f"  2025 median: ${age29.get('p50', 0):,.0f}  "
              f"(×{get_growth_factor(29):.3f})")

    # Write
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\nWrote {output_path}")
    print(f"  Years now: {sorted(data['data'].keys())}")
    print(f"  2025 ages: {len(data['data']['2025'])} "
          f"({min(data['data']['2025'].keys())}–{max(data['data']['2025'].keys())})")
    print(f"\n  Note: 2025 data is ESTIMATED. Flagged with estimated=true in each record.")


if __name__ == '__main__':
    main()
