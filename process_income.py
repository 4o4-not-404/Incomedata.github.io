#!/usr/bin/env python3
"""
process_income.py — Compute income percentiles by age and year from IPUMS-CPS ASEC microdata.

Input:  cps_asec.csv.gz (IPUMS-CPS extract with AGE, INCTOT, ASECWT, YEAR, EMPSTAT)
Output: income_percentiles.json (structured percentile data for visualization)

Methodology follows DQYDJ.com's approach:
  - Uses ASECWT (ASEC supplement weight) for all computations
  - Worker screen: includes employed + unemployed (looking for work)
  - Income: INCTOT (total personal income, all sources, pre-tax)
  - Excludes negative/zero income by default (configurable)
  - Computes weighted percentiles using linear interpolation

Usage:
    python process_income.py                          # defaults
    python process_income.py --input my_extract.csv   # custom input
    python process_income.py --no-worker-screen       # include all persons
    python process_income.py --include-zero            # include zero income
"""

import argparse
import json
import sys
import os
import time
from pathlib import Path

import numpy as np
import pandas as pd


# ── CPI-U Annual Averages (BLS Series CUUR0000SA0) ──────────────────────
# Used for inflation adjustment. Base year is configurable.
CPI_U = {
    1990: 130.7, 1991: 136.2, 1992: 140.3, 1993: 144.5, 1994: 148.2,
    1995: 152.4, 1996: 156.9, 1997: 160.5, 1998: 163.0, 1999: 166.6,
    2000: 172.2, 2001: 177.1, 2002: 179.9, 2003: 184.0, 2004: 188.9,
    2005: 195.3, 2006: 201.6, 2007: 207.3, 2008: 215.3, 2009: 214.5,
    2010: 218.1, 2011: 224.9, 2012: 229.6, 2013: 233.0, 2014: 236.7,
    2015: 237.0, 2016: 240.0, 2017: 245.1, 2018: 251.1, 2019: 255.7,
    2020: 258.8, 2021: 270.9, 2022: 292.7, 2023: 304.7, 2024: 313.0,
    2025: 320.0,  # estimate; update when BLS publishes
}

# IPUMS EMPSTAT codes
EMPLOYED_CODES = {10, 12}       # At work, Has job not at work
UNEMPLOYED_CODES = {20, 21, 22} # Unemployed (experienced + new)
NILF_CODES = {30, 31, 32, 33, 34, 35, 36}  # Not in labor force

PERCENTILES = [1, 5, 10, 25, 50, 75, 90, 95, 99]


def weighted_percentile(values, weights, percentile):
    """
    Compute a weighted percentile using linear interpolation.

    This matches the standard approach used by DQYDJ and most survey
    statisticians for weighted microdata.
    """
    # Sort by value
    idx = np.argsort(values)
    sorted_vals = values[idx]
    sorted_wts = weights[idx]

    # Cumulative weight
    cum_wt = np.cumsum(sorted_wts)
    total_wt = cum_wt[-1]

    # Target cumulative weight for this percentile
    target = percentile / 100.0 * total_wt

    # Find position via interpolation
    if target <= cum_wt[0]:
        return sorted_vals[0]
    if target >= cum_wt[-1]:
        return sorted_vals[-1]

    # Linear interpolation between bracketing observations
    i = np.searchsorted(cum_wt, target, side='left')
    if i == 0:
        return sorted_vals[0]

    # Interpolate
    w_below = cum_wt[i - 1]
    w_above = cum_wt[i]
    if w_above == w_below:
        return sorted_vals[i]

    fraction = (target - w_below) / (w_above - w_below)
    return sorted_vals[i - 1] + fraction * (sorted_vals[i] - sorted_vals[i - 1])


def weighted_mean(values, weights):
    """Compute weighted mean."""
    return np.average(values, weights=weights)


def detect_income_year(survey_year):
    """
    IPUMS CPS ASEC: the survey conducted in March of year Y asks about
    income earned in year Y-1. So YEAR=2025 means income year 2024.
    """
    return survey_year - 1


def load_and_validate(filepath):
    """Load the IPUMS extract and validate required columns."""
    print(f"Loading {filepath}...")

    # IPUMS CSV files can be large; read in chunks if needed
    # Try common compression formats
    if str(filepath).endswith('.gz'):
        df = pd.read_csv(filepath, compression='gzip')
    elif str(filepath).endswith('.zip'):
        df = pd.read_csv(filepath, compression='zip')
    else:
        df = pd.read_csv(filepath)

    # IPUMS uses uppercase column names
    df.columns = df.columns.str.upper()

    required = {'AGE', 'INCTOT', 'ASECWT', 'YEAR'}
    missing = required - set(df.columns)
    if missing:
        # Try alternate weight names
        if 'WTSUPP' in df.columns and 'ASECWT' in missing:
            print("  Note: Using WTSUPP as ASECWT (older IPUMS naming)")
            df['ASECWT'] = df['WTSUPP']
            missing.discard('ASECWT')
        if missing:
            print(f"ERROR: Missing required columns: {missing}")
            print(f"  Available columns: {sorted(df.columns.tolist())}")
            sys.exit(1)

    print(f"  Loaded {len(df):,} person records")
    print(f"  Survey years: {sorted(df['YEAR'].unique())}")
    print(f"  Age range: {df['AGE'].min()}–{df['AGE'].max()}")

    return df


def apply_worker_screen(df, include_all=False):
    """
    Apply the worker screen following DQYDJ methodology.

    Default: include people who were employed OR unemployed (looking for work)
    in the reference year. Excludes NILF (not in labor force).
    """
    if include_all:
        print("  Worker screen: DISABLED (including all persons)")
        return df

    if 'EMPSTAT' in df.columns:
        worker_codes = EMPLOYED_CODES | UNEMPLOYED_CODES
        mask = df['EMPSTAT'].isin(worker_codes)
        filtered = df[mask].copy()
        print(f"  Worker screen: {len(filtered):,} of {len(df):,} "
              f"({len(filtered)/len(df)*100:.1f}%) — employed + unemployed")
        return filtered
    else:
        print("  WARNING: EMPSTAT not in extract. Cannot apply worker screen.")
        print("  Proceeding with all persons. For accurate results, re-extract")
        print("  from IPUMS with EMPSTAT included.")
        return df


def filter_income(df, include_zero=False):
    """
    Filter income values.

    IPUMS codes:
      - 99999999 = N.I.U. (not in universe) — must exclude
      - 99999998 = Missing — must exclude
      - Negative values = losses (business, farm) — exclude by default
      - Zero = no income — exclude by default (following DQYDJ)
    """
    n_before = len(df)

    # Exclude NIU and missing
    df = df[~df['INCTOT'].isin([99999999, 99999998])].copy()

    if include_zero:
        df = df[df['INCTOT'] >= 0].copy()
        print(f"  Income filter: {len(df):,} of {n_before:,} "
              f"(excluding NIU/missing, keeping zero)")
    else:
        df = df[df['INCTOT'] > 0].copy()
        print(f"  Income filter: {len(df):,} of {n_before:,} "
              f"(excluding NIU/missing/zero/negative)")

    return df


def compute_percentiles(df, age_min=16, age_max=75):
    """
    Compute weighted percentiles for every year × age combination.

    Returns a nested dict: {income_year: {age: {stats}}}
    """
    results = {}

    years = sorted(df['YEAR'].unique())
    print(f"\nComputing percentiles for {len(years)} survey years, "
          f"ages {age_min}–{age_max}...")

    for survey_year in years:
        income_year = detect_income_year(survey_year)
        year_df = df[df['YEAR'] == survey_year]

        year_data = {}

        for age in range(age_min, age_max + 1):
            age_df = year_df[year_df['AGE'] == age]

            if len(age_df) < 25:
                # Too few observations for meaningful percentile computation
                continue

            values = age_df['INCTOT'].values.astype(float)
            weights = age_df['ASECWT'].values.astype(float)

            # Exclude zero/negative weights
            valid = weights > 0
            values = values[valid]
            weights = weights[valid]

            if len(values) < 25:
                continue

            stats = {
                'n_samples': int(len(values)),
                'est_workforce': int(np.sum(weights)),
                'mean': round(float(weighted_mean(values, weights)), 2),
            }

            for p in PERCENTILES:
                stats[f'p{p}'] = round(float(weighted_percentile(values, weights, p)), 2)

            year_data[age] = stats

        results[income_year] = year_data
        n_ages = len(year_data)
        print(f"  Income year {income_year} (survey {survey_year}): "
              f"{n_ages} ages computed")

    return results


def build_output(results):
    """
    Build the final output structure with metadata.
    """
    output = {
        'metadata': {
            'description': 'U.S. individual income percentiles by age and year',
            'source': 'Census Bureau CPS ASEC via IPUMS-CPS',
            'methodology': {
                'income_variable': 'INCTOT (total personal income, all sources)',
                'weight_variable': 'ASECWT (ASEC supplement person weight)',
                'population': 'Workers (employed + unemployed/looking for work)',
                'income_type': 'Gross (pre-tax)',
                'income_exclusions': 'NIU, missing, zero, and negative values excluded',
                'percentile_method': 'Weighted linear interpolation',
            },
            'percentiles_computed': PERCENTILES,
            'cpi_u': CPI_U,
            'citation': (
                'Sarah Flood, Miriam King, Renae Rodgers, Steven Ruggles, '
                'J. Robert Warren, et al. IPUMS CPS: Version 13.0 [dataset]. '
                'Minneapolis, MN: IPUMS, 2025. https://doi.org/10.18128/D030.V13.0'
            ),
            'generated_at': time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime()),
        },
        'data': {},
    }

    # Convert integer keys to strings for JSON
    for income_year, age_data in sorted(results.items()):
        output['data'][str(income_year)] = {
            str(age): stats for age, stats in sorted(age_data.items())
        }

    return output


def print_summary(results):
    """Print a summary of the computed data."""
    years = sorted(results.keys())
    print(f"\n{'='*70}")
    print(f"SUMMARY")
    print(f"{'='*70}")
    print(f"Income years covered: {years[0]}–{years[-1]} ({len(years)} years)")

    # Show age 29 as an example
    print(f"\nExample: Age 29 over time")
    print(f"{'Year':>6} {'Median':>10} {'75th':>10} {'90th':>10} {'99th':>12} {'Samples':>8}")
    print(f"{'-'*6} {'-'*10} {'-'*10} {'-'*10} {'-'*12} {'-'*8}")

    for yr in years:
        if 29 in results[yr]:
            d = results[yr][29]
            print(f"{yr:>6} "
                  f"${d['p50']:>9,.0f} "
                  f"${d['p75']:>9,.0f} "
                  f"${d['p90']:>9,.0f} "
                  f"${d['p99']:>11,.0f} "
                  f"{d['n_samples']:>8,}")

    print(f"\nOutput written to income_percentiles.json")


def main():
    parser = argparse.ArgumentParser(
        description='Compute income percentiles by age from IPUMS-CPS ASEC data'
    )
    parser.add_argument(
        '--input', '-i',
        default=None,
        help='Path to IPUMS CSV extract (default: auto-detect cps_asec.csv[.gz])'
    )
    parser.add_argument(
        '--output', '-o',
        default='income_percentiles.json',
        help='Output JSON path (default: income_percentiles.json)'
    )
    parser.add_argument(
        '--no-worker-screen',
        action='store_true',
        help='Include all persons, not just workers'
    )
    parser.add_argument(
        '--include-zero',
        action='store_true',
        help='Include zero-income workers'
    )
    parser.add_argument(
        '--age-min', type=int, default=16,
        help='Minimum age (default: 16)'
    )
    parser.add_argument(
        '--age-max', type=int, default=75,
        help='Maximum age (default: 75)'
    )

    args = parser.parse_args()

    # Find input file
    if args.input:
        filepath = Path(args.input)
    else:
        candidates = [
            'cps_asec.csv.gz', 'cps_asec.csv', 'cps_asec.dat.gz',
            'cps_00001.csv.gz', 'cps_00001.csv',  # IPUMS default naming
        ]
        filepath = None
        for c in candidates:
            if Path(c).exists():
                filepath = Path(c)
                break
        if filepath is None:
            print("ERROR: No input file found.")
            print(f"  Looked for: {', '.join(candidates)}")
            print("  Download your IPUMS extract and place it in this directory,")
            print("  or specify the path with --input")
            sys.exit(1)

    if not filepath.exists():
        print(f"ERROR: File not found: {filepath}")
        sys.exit(1)

    print(f"{'='*70}")
    print(f"IPUMS-CPS Income Percentile Processor")
    print(f"{'='*70}")

    # Load
    df = load_and_validate(filepath)

    # Apply filters
    df = apply_worker_screen(df, include_all=args.no_worker_screen)
    df = filter_income(df, include_zero=args.include_zero)

    # Compute
    results = compute_percentiles(df, args.age_min, args.age_max)

    # Build output
    output = build_output(results)

    # Write JSON
    with open(args.output, 'w') as f:
        json.dump(output, f, indent=2)

    print_summary(results)

    # Also write a flat CSV for easy inspection
    csv_path = Path(args.output).with_suffix('.csv')
    rows = []
    for income_year, age_data in sorted(results.items()):
        for age, stats in sorted(age_data.items()):
            row = {'income_year': income_year, 'age': age}
            row.update(stats)
            rows.append(row)
    pd.DataFrame(rows).to_csv(csv_path, index=False)
    print(f"Also wrote flat CSV: {csv_path}")


if __name__ == '__main__':
    main()
