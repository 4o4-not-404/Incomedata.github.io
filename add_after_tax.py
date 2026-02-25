#!/usr/bin/env python3
"""
add_after_tax.py — Post-process income_percentiles.json to add after-tax estimates.

Applies a simplified tax model to each year × age × percentile value:
  - Federal income tax (actual brackets for single filer, 1995–2025)
  - FICA (Social Security + Medicare employee share, with annual wage base)
  - Average state income tax (flat effective rate on taxable income)

Since the tax function is monotonically increasing, percentile ordering is
preserved: after_tax_pX = gross_pX - tax(gross_pX). This is exact for
percentiles. The after-tax mean is approximate (applies tax to the pre-tax
mean; Jensen's inequality means the true after-tax mean is slightly higher).

Usage:
    python add_after_tax.py
    python add_after_tax.py --state-rate 0.04
    python add_after_tax.py --no-state
"""

import argparse
import json
import sys
from pathlib import Path


# ═══════════════════════════════════════════════════════════════════════════
# FEDERAL INCOME TAX BRACKETS (Single Filer)
# Each year maps to list of (threshold, marginal_rate) tuples.
# Income from 0 to first threshold taxed at first rate, etc.
# ═══════════════════════════════════════════════════════════════════════════

FEDERAL_BRACKETS = {
    # ── Pre-EGTRRA: 15/28/31/36/39.6 ──
    1995: [(0, 0.15), (23350, 0.28), (56550, 0.31), (117950, 0.36), (256500, 0.396)],
    1996: [(0, 0.15), (24000, 0.28), (58150, 0.31), (121300, 0.36), (263750, 0.396)],
    1997: [(0, 0.15), (24650, 0.28), (59750, 0.31), (124650, 0.36), (271050, 0.396)],
    1998: [(0, 0.15), (25350, 0.28), (61400, 0.31), (128100, 0.36), (278450, 0.396)],
    1999: [(0, 0.15), (25750, 0.28), (62450, 0.31), (130250, 0.36), (283150, 0.396)],
    2000: [(0, 0.15), (26250, 0.28), (63550, 0.31), (132600, 0.36), (288350, 0.396)],
    # ── EGTRRA transition ──
    2001: [(0, 0.10), (6000, 0.15), (27050, 0.275), (65550, 0.305), (136750, 0.355), (297350, 0.391)],
    2002: [(0, 0.10), (6000, 0.15), (27950, 0.27), (67700, 0.30), (141250, 0.35), (307050, 0.386)],
    # ── JGTRRA: 10/15/25/28/33/35 ──
    2003: [(0, 0.10), (7000, 0.15), (28400, 0.25), (68800, 0.28), (143500, 0.33), (311950, 0.35)],
    2004: [(0, 0.10), (7150, 0.15), (29050, 0.25), (70350, 0.28), (146750, 0.33), (319100, 0.35)],
    2005: [(0, 0.10), (7300, 0.15), (29700, 0.25), (71950, 0.28), (150150, 0.33), (326450, 0.35)],
    2006: [(0, 0.10), (7550, 0.15), (30650, 0.25), (74200, 0.28), (154800, 0.33), (336550, 0.35)],
    2007: [(0, 0.10), (7825, 0.15), (31850, 0.25), (77100, 0.28), (160850, 0.33), (349700, 0.35)],
    2008: [(0, 0.10), (8025, 0.15), (32550, 0.25), (78850, 0.28), (164550, 0.33), (357700, 0.35)],
    2009: [(0, 0.10), (8350, 0.15), (33950, 0.25), (82250, 0.28), (171550, 0.33), (372950, 0.35)],
    2010: [(0, 0.10), (8375, 0.15), (34000, 0.25), (82400, 0.28), (171850, 0.33), (373650, 0.35)],
    2011: [(0, 0.10), (8500, 0.15), (34500, 0.25), (83600, 0.28), (174400, 0.33), (379150, 0.35)],
    2012: [(0, 0.10), (8700, 0.15), (35350, 0.25), (85650, 0.28), (178650, 0.33), (388350, 0.35)],
    # ── ATRA: added 39.6% bracket ──
    2013: [(0, 0.10), (8925, 0.15), (36250, 0.25), (87850, 0.28), (183250, 0.33), (398350, 0.35), (400000, 0.396)],
    2014: [(0, 0.10), (9075, 0.15), (36900, 0.25), (89350, 0.28), (186350, 0.33), (405100, 0.35), (406750, 0.396)],
    2015: [(0, 0.10), (9225, 0.15), (37450, 0.25), (90750, 0.28), (189300, 0.33), (411500, 0.35), (413200, 0.396)],
    2016: [(0, 0.10), (9275, 0.15), (37650, 0.25), (91150, 0.28), (190150, 0.33), (413350, 0.35), (415050, 0.396)],
    2017: [(0, 0.10), (9325, 0.15), (37950, 0.25), (91900, 0.28), (191650, 0.33), (416700, 0.35), (418400, 0.396)],
    # ── TCJA: 10/12/22/24/32/35/37 ──
    2018: [(0, 0.10), (9525, 0.12), (38700, 0.22), (82500, 0.24), (157500, 0.32), (200000, 0.35), (500000, 0.37)],
    2019: [(0, 0.10), (9700, 0.12), (39475, 0.22), (84200, 0.24), (160725, 0.32), (204100, 0.35), (510300, 0.37)],
    2020: [(0, 0.10), (9875, 0.12), (40125, 0.22), (85525, 0.24), (163300, 0.32), (207350, 0.35), (518400, 0.37)],
    2021: [(0, 0.10), (9950, 0.12), (40525, 0.22), (86375, 0.24), (164925, 0.32), (209425, 0.35), (523600, 0.37)],
    2022: [(0, 0.10), (10275, 0.12), (41775, 0.22), (89075, 0.24), (170050, 0.32), (215950, 0.35), (539900, 0.37)],
    2023: [(0, 0.10), (11000, 0.12), (44725, 0.22), (95375, 0.24), (182100, 0.32), (231250, 0.35), (578125, 0.37)],
    2024: [(0, 0.10), (11600, 0.12), (47150, 0.22), (100525, 0.24), (191950, 0.32), (243725, 0.35), (609350, 0.37)],
    2025: [(0, 0.10), (11925, 0.12), (48475, 0.22), (103350, 0.24), (197300, 0.32), (250525, 0.35), (626350, 0.37)],
}

# ═══════════════════════════════════════════════════════════════════════════
# STANDARD DEDUCTION + PERSONAL EXEMPTION (Single Filer)
# Pre-2018: standard deduction + personal exemption
# 2018+: TCJA doubled the standard deduction, eliminated personal exemption
# ═══════════════════════════════════════════════════════════════════════════

STANDARD_DEDUCTION = {
    1995: 3900, 1996: 4000, 1997: 4150, 1998: 4250, 1999: 4300,
    2000: 4400, 2001: 4550, 2002: 4700, 2003: 4750, 2004: 4850,
    2005: 5000, 2006: 5150, 2007: 5350, 2008: 5450, 2009: 5700,
    2010: 5700, 2011: 5800, 2012: 5950, 2013: 6100, 2014: 6200,
    2015: 6300, 2016: 6300, 2017: 6350,
    2018: 12000, 2019: 12200, 2020: 12400, 2021: 12550, 2022: 12950,
    2023: 13850, 2024: 14600, 2025: 15000,
}

PERSONAL_EXEMPTION = {
    1995: 2500, 1996: 2550, 1997: 2650, 1998: 2700, 1999: 2750,
    2000: 2800, 2001: 2900, 2002: 3000, 2003: 3050, 2004: 3100,
    2005: 3200, 2006: 3300, 2007: 3400, 2008: 3500, 2009: 3650,
    2010: 3650, 2011: 3700, 2012: 3800, 2013: 3900, 2014: 3950,
    2015: 4000, 2016: 4050, 2017: 4050,
    # TCJA eliminated personal exemption
    2018: 0, 2019: 0, 2020: 0, 2021: 0, 2022: 0,
    2023: 0, 2024: 0, 2025: 0,
}

# ═══════════════════════════════════════════════════════════════════════════
# FICA: Social Security + Medicare (Employee Share)
# ═══════════════════════════════════════════════════════════════════════════

SS_WAGE_BASE = {
    1995: 61200,  1996: 62700,  1997: 65400,  1998: 68400,  1999: 72600,
    2000: 76200,  2001: 80400,  2002: 84900,  2003: 87000,  2004: 87900,
    2005: 90000,  2006: 94200,  2007: 97500,  2008: 102000, 2009: 106800,
    2010: 106800, 2011: 106800, 2012: 110100, 2013: 113700, 2014: 117000,
    2015: 118500, 2016: 118500, 2017: 127200, 2018: 128400, 2019: 132900,
    2020: 137700, 2021: 142800, 2022: 147000, 2023: 160200, 2024: 168600,
    2025: 176100,
}

# Employee SS rate: 6.2% except during 2011-2012 payroll tax holiday (4.2%)
SS_RATE = {yr: 0.062 for yr in range(1995, 2026)}
SS_RATE[2011] = 0.042
SS_RATE[2012] = 0.042

MEDICARE_RATE = 0.0145  # 1.45%, no cap
# Additional Medicare Tax: 0.9% on earned income > $200k, starting 2013
ADDITIONAL_MEDICARE_THRESHOLD = 200000
ADDITIONAL_MEDICARE_RATE = 0.009
ADDITIONAL_MEDICARE_START_YEAR = 2013

# Average state income tax rate (population-weighted across all states,
# including states with no income tax). Configurable via --state-rate.
DEFAULT_STATE_RATE = 0.05


# ═══════════════════════════════════════════════════════════════════════════
# TAX COMPUTATION
# ═══════════════════════════════════════════════════════════════════════════

def compute_federal_tax(gross_income, year):
    """
    Compute federal income tax for a single filer.

    Applies standard deduction + personal exemption, then bracket rates.
    Returns tax liability (>= 0).
    """
    if gross_income <= 0:
        return 0.0

    year = max(1995, min(2025, year))
    std_ded = STANDARD_DEDUCTION[year]
    pers_exempt = PERSONAL_EXEMPTION[year]
    taxable = max(0, gross_income - std_ded - pers_exempt)

    if taxable <= 0:
        return 0.0

    brackets = FEDERAL_BRACKETS[year]
    tax = 0.0

    for i, (threshold, rate) in enumerate(brackets):
        if i + 1 < len(brackets):
            next_threshold = brackets[i + 1][0]
            bracket_income = min(taxable, next_threshold) - threshold
        else:
            bracket_income = taxable - threshold

        if bracket_income > 0:
            tax += bracket_income * rate

        if i + 1 < len(brackets) and taxable <= brackets[i + 1][0]:
            break

    return tax


def compute_fica(gross_income, year):
    """
    Compute FICA taxes (employee share).

    Social Security: rate × min(income, wage_base)
    Medicare: 1.45% on all income + 0.9% on income > $200k (2013+)

    Note: FICA technically applies only to earned income (wages/salary),
    not investment income. Since we only have INCTOT (total income), this
    overstates FICA for people with significant non-wage income. The
    distortion is small for most of the distribution where wages dominate.
    """
    if gross_income <= 0:
        return 0.0

    year = max(1995, min(2025, year))

    # Social Security
    ss_income = min(gross_income, SS_WAGE_BASE[year])
    ss_tax = ss_income * SS_RATE[year]

    # Medicare
    medicare_tax = gross_income * MEDICARE_RATE

    # Additional Medicare Tax (2013+)
    if year >= ADDITIONAL_MEDICARE_START_YEAR and gross_income > ADDITIONAL_MEDICARE_THRESHOLD:
        medicare_tax += (gross_income - ADDITIONAL_MEDICARE_THRESHOLD) * ADDITIONAL_MEDICARE_RATE

    return ss_tax + medicare_tax


def compute_state_tax(gross_income, year, rate=DEFAULT_STATE_RATE):
    """
    Estimate average state income tax.

    Uses a flat effective rate on (income - federal standard deduction) as
    a population-weighted average across all states (including those with
    no income tax). Default 5% is a reasonable approximation.
    """
    if gross_income <= 0 or rate <= 0:
        return 0.0

    year = max(1995, min(2025, year))
    # Use federal standard deduction as proxy for state deductions
    taxable = max(0, gross_income - STANDARD_DEDUCTION[year])
    return taxable * rate


def compute_after_tax(gross_income, year, state_rate=DEFAULT_STATE_RATE):
    """
    Compute after-tax income = gross - federal - FICA - state.

    Returns (after_tax_income, tax_detail_dict).
    """
    if gross_income <= 0:
        return gross_income, {'federal': 0, 'fica': 0, 'state': 0, 'total': 0}

    federal = compute_federal_tax(gross_income, year)
    fica = compute_fica(gross_income, year)
    state = compute_state_tax(gross_income, year, state_rate)
    total_tax = federal + fica + state

    # Floor at zero (shouldn't happen with positive income, but safety)
    after_tax = max(0, gross_income - total_tax)

    return after_tax, {
        'federal': round(federal, 2),
        'fica': round(fica, 2),
        'state': round(state, 2),
        'total': round(total_tax, 2),
        'effective_rate': round(total_tax / gross_income, 4) if gross_income > 0 else 0,
    }


# ═══════════════════════════════════════════════════════════════════════════
# POST-PROCESSING
# ═══════════════════════════════════════════════════════════════════════════

INCOME_FIELDS = ['mean', 'p1', 'p5', 'p10', 'p25', 'p50', 'p75', 'p90', 'p95', 'p99']


def add_after_tax_to_data(data, state_rate=DEFAULT_STATE_RATE):
    """
    Add after-tax fields to every year × age record in the data.

    For each field 'pXX' or 'mean', adds 'at_pXX' or 'at_mean' with the
    after-tax value, plus 'at_effective_rate' at the median income level.

    Because the tax function is monotonically increasing, percentile ordering
    is preserved and after_tax_pX = gross_pX - tax(gross_pX) is exact.
    The after-tax mean is approximate (see module docstring).
    """
    years_processed = 0
    records_processed = 0

    for year_str, age_data in data['data'].items():
        year = int(year_str)

        for age_str, record in age_data.items():
            for field in INCOME_FIELDS:
                if field in record and record[field] is not None:
                    gross = record[field]
                    at_val, _ = compute_after_tax(gross, year, state_rate)
                    record[f'at_{field}'] = round(at_val, 2)

            # Store effective total tax rate at the median for quick reference
            if 'p50' in record and record['p50'] is not None and record['p50'] > 0:
                _, detail = compute_after_tax(record['p50'], year, state_rate)
                record['at_effective_rate_p50'] = detail['effective_rate']

            records_processed += 1

        years_processed += 1

    return years_processed, records_processed


def add_tax_metadata(data, state_rate):
    """Add tax model metadata to the output."""
    data['metadata']['after_tax_model'] = {
        'description': 'Estimated after-tax income using simplified tax model',
        'components': {
            'federal': 'Actual single-filer brackets + standard deduction + personal exemption by year',
            'fica': 'Employee share: SS (6.2% to wage base, 4.2% in 2011-12) + Medicare (1.45%) + Addl Medicare (0.9% >$200k, 2013+)',
            'state': f'Flat {state_rate*100:.1f}% effective rate on (income - std deduction) as population-weighted average',
        },
        'assumptions': [
            'Single filer with standard deduction (no itemizing)',
            'FICA applied to total income (overstates for those with significant non-wage income)',
            'No tax credits (EITC, child credit, etc.) — understates after-tax income for lower brackets',
            'State tax is a national average; actual varies ~0-13% by state',
            'After-tax percentiles are exact; after-tax mean is approximate',
        ],
        'state_rate_used': state_rate,
        'field_prefix': 'at_',
    }


def print_sanity_check(data):
    """Print a sanity check of tax rates at various income levels."""
    print(f"\n{'='*70}")
    print("SANITY CHECK — Effective total tax rates (federal + FICA + state)")
    print(f"{'='*70}")

    check_years = [1995, 2000, 2005, 2010, 2015, 2020, 2024, 2025]
    check_years = [y for y in check_years if str(y) in data['data']]

    incomes = [25000, 50000, 75000, 100000, 150000, 250000]

    header = f"{'Income':>10}  " + "  ".join(f"{y:>6}" for y in check_years)
    print(header)
    print("-" * len(header))

    for inc in incomes:
        rates = []
        for y in check_years:
            _, detail = compute_after_tax(inc, y)
            rates.append(f"{detail['effective_rate']*100:5.1f}%")
        print(f"${inc:>9,}  " + "  ".join(rates))

    # Show age 29 median before/after
    print(f"\nAge 29, median income — before and after tax:")
    print(f"{'Year':>6} {'Pre-tax':>10} {'After-tax':>10} {'Eff Rate':>10}")
    for y in check_years:
        rec = data['data'].get(str(y), {}).get('29', {})
        if rec and 'p50' in rec and 'at_p50' in rec:
            eff = rec.get('at_effective_rate_p50', 0)
            print(f"{y:>6} ${rec['p50']:>9,.0f} ${rec['at_p50']:>9,.0f} {eff*100:>9.1f}%")


def main():
    parser = argparse.ArgumentParser(
        description='Add after-tax income estimates to income_percentiles.json'
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
    parser.add_argument(
        '--state-rate',
        type=float,
        default=DEFAULT_STATE_RATE,
        help=f'Average state income tax rate (default: {DEFAULT_STATE_RATE})'
    )
    parser.add_argument(
        '--no-state',
        action='store_true',
        help='Exclude state income tax'
    )

    args = parser.parse_args()
    output_path = args.output or args.input
    state_rate = 0.0 if args.no_state else args.state_rate

    # Load
    print(f"Loading {args.input}...")
    with open(args.input) as f:
        data = json.load(f)

    years = sorted(data['data'].keys())
    print(f"  Years: {years[0]}–{years[-1]} ({len(years)} years)")

    # Process
    print(f"\nApplying tax model (state rate: {state_rate*100:.1f}%)...")
    n_years, n_records = add_after_tax_to_data(data, state_rate)
    print(f"  Processed {n_records:,} year×age records across {n_years} years")

    # Add metadata
    add_tax_metadata(data, state_rate)

    # Sanity check
    print_sanity_check(data)

    # Write
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"\nWrote {output_path}")

    # Also update CSV if it exists
    csv_path = Path(output_path).with_suffix('.csv')
    if csv_path.exists():
        import pandas as pd
        rows = []
        for year_str, age_data in sorted(data['data'].items()):
            for age_str, stats in sorted(age_data.items(), key=lambda x: int(x[0])):
                row = {'income_year': int(year_str), 'age': int(age_str)}
                row.update(stats)
                rows.append(row)
        pd.DataFrame(rows).to_csv(csv_path, index=False)
        print(f"Updated CSV: {csv_path}")


if __name__ == '__main__':
    main()
