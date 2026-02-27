"""
Historical U.S. Federal Tax Data for Single Filers, 1961-1994.

Sources:
  - Tax brackets: tax-brackets.org archived federal tax tables
  - Tax Foundation: Historical Federal Individual Income Tax Rates & Brackets
  - SSA: Social Security wage base and FICA rates (ssa.gov/oact/progdata/taxRates.html)
  - Tax Policy Center: Historical Social Security tax rates (ssrate_historical)
  - Milefoot.com: Historical FICA Tax Information
  - IRS: Historical standard deduction and personal exemption data

Each year entry contains:
  'brackets': list of (upper_bound_of_bracket, marginal_rate) tuples.
              The last tuple uses float('inf') for the top bracket.
              Rates are expressed as decimals (e.g., 0.20 = 20%).
              IMPORTANT: All brackets are normalized to apply to TAXABLE INCOME
              (i.e., income AFTER subtracting standard_deduction and
              personal_exemption). For 1977-1986, the original IRS rate tables
              included a "zero bracket amount" (ZBA); here, that ZBA offset has
              been removed from bracket thresholds so the convention is uniform
              across all years.
  'standard_deduction': Standard deduction (or equivalent ZBA) for single filers.
  'personal_exemption': Personal exemption amount in dollars.
  'ss_wage_base': Social Security (OASDI) maximum taxable earnings.
  'ss_rate': Social Security (OASDI) employee tax rate as decimal.
  'medicare_rate': Medicare (HI) employee tax rate as decimal (0.0 before 1966).

Notes:
  - 1961-1963: Pre-Revenue Act of 1964 rates; top rate 91%.
  - 1963: Transitional rates from Revenue Act of 1964 (rates effective mid-year
    for some provisions; brackets shown here are the full-year 1963 rates).
  - 1964: Revenue Act of 1964 Phase I rates.
  - 1965-1969: Revenue Act of 1964 permanent rates (top rate 70%).
  - 1970-1975: Same bracket structure as 1965-1969 for single filers.
  - 1971: Tax Reform Act of 1969 introduced separate single-filer rate schedules.
  - 1976-1977: Standard deduction incorporated into a "zero bracket amount" built
    into the rate tables. Brackets shown start at the zero-bracket threshold.
  - 1978-1981: Revenue Act of 1978 restructured brackets.
  - 1982-1986: Economic Recovery Tax Act of 1981 (ERTA) reduced rates in stages.
  - 1987: Tax Reform Act of 1986 collapsed to 2 brackets (15%/28%) + bubble.
  - 1988-1990: Two-bracket system (15%/28%), with 1990 adding 31% bracket.
  - 1991-1992: Three brackets (15%/28%/31%).
  - 1993-1994: OBRA 1993 added 36% and 39.6% brackets.

  - Medicare (HI) tax began in 1966 at 0.35% employee rate.
  - Before 1966, there was no separate Medicare tax.
  - Before 1991, the combined FICA rate shown at milefoot.com includes both
    OASDI and HI; the separate rates below are from SSA actuarial tables.
  - In 1994, the Medicare (HI) wage base cap was removed (became unlimited).

  - For 1961-1970, the "standard deduction" was 10% of AGI with a cap
    (typically $1,000 for single filers). From 1970 onward, a flat dollar
    amount or a "low income allowance" applied instead. The amounts below
    represent the basic standard deduction available to a single filer.
  - In 1977-1986, the "zero bracket amount" was built into the tax tables;
    the standard_deduction field here reflects the equivalent value.
"""

TAX_DATA = {
    # =========================================================================
    # 1961-1963: Pre-Revenue Act of 1964 (top rate 91%)
    # Standard deduction: 10% of AGI, max $1,000 for single
    # Personal exemption: $600
    # =========================================================================
    1961: {
        'brackets': [
            (2000, 0.20),
            (4000, 0.22),
            (6000, 0.26),
            (8000, 0.30),
            (10000, 0.34),
            (12000, 0.38),
            (14000, 0.43),
            (16000, 0.47),
            (18000, 0.50),
            (20000, 0.53),
            (22000, 0.56),
            (26000, 0.59),
            (32000, 0.62),
            (38000, 0.65),
            (44000, 0.69),
            (50000, 0.72),
            (60000, 0.75),
            (70000, 0.78),
            (80000, 0.81),
            (90000, 0.84),
            (100000, 0.87),
            (150000, 0.89),
            (200000, 0.90),
            (float('inf'), 0.91),
        ],
        'standard_deduction': 1000,
        'personal_exemption': 600,
        'ss_wage_base': 4800,
        'ss_rate': 0.03,
        'medicare_rate': 0.0,
    },
    1962: {
        'brackets': [
            (2000, 0.20),
            (4000, 0.22),
            (6000, 0.26),
            (8000, 0.30),
            (10000, 0.34),
            (12000, 0.38),
            (14000, 0.43),
            (16000, 0.47),
            (18000, 0.50),
            (20000, 0.53),
            (22000, 0.56),
            (26000, 0.59),
            (32000, 0.62),
            (38000, 0.65),
            (44000, 0.69),
            (50000, 0.72),
            (60000, 0.75),
            (70000, 0.78),
            (80000, 0.81),
            (90000, 0.84),
            (100000, 0.87),
            (150000, 0.89),
            (200000, 0.90),
            (float('inf'), 0.91),
        ],
        'standard_deduction': 1000,
        'personal_exemption': 600,
        'ss_wage_base': 4800,
        'ss_rate': 0.03125,
        'medicare_rate': 0.0,
    },
    1963: {
        'brackets': [
            (500, 0.16),
            (1000, 0.17),
            (1500, 0.18),
            (2000, 0.18),
            (4000, 0.20),
            (6000, 0.24),
            (8000, 0.27),
            (10000, 0.31),
            (12000, 0.34),
            (14000, 0.38),
            (16000, 0.41),
            (18000, 0.45),
            (20000, 0.48),
            (22000, 0.51),
            (26000, 0.54),
            (32000, 0.56),
            (38000, 0.59),
            (44000, 0.61),
            (50000, 0.64),
            (60000, 0.66),
            (70000, 0.69),
            (80000, 0.71),
            (90000, 0.74),
            (100000, 0.75),
            (float('inf'), 0.77),
        ],
        'standard_deduction': 1000,
        'personal_exemption': 600,
        'ss_wage_base': 4800,
        'ss_rate': 0.03625,
        'medicare_rate': 0.0,
    },

    # =========================================================================
    # 1964: Revenue Act of 1964 Phase I (transitional rates)
    # =========================================================================
    1964: {
        'brackets': [
            (500, 0.14),
            (1000, 0.15),
            (1500, 0.16),
            (2000, 0.17),
            (4000, 0.19),
            (6000, 0.22),
            (8000, 0.25),
            (10000, 0.28),
            (12000, 0.32),
            (14000, 0.36),
            (16000, 0.39),
            (18000, 0.42),
            (20000, 0.45),
            (22000, 0.48),
            (26000, 0.50),
            (32000, 0.53),
            (38000, 0.55),
            (44000, 0.58),
            (50000, 0.60),
            (60000, 0.62),
            (70000, 0.64),
            (80000, 0.66),
            (90000, 0.68),
            (100000, 0.69),
            (float('inf'), 0.70),
        ],
        'standard_deduction': 1000,
        'personal_exemption': 600,
        'ss_wage_base': 4800,
        'ss_rate': 0.03625,
        'medicare_rate': 0.0,
    },

    # =========================================================================
    # 1965-1969: Revenue Act of 1964 permanent rates (top rate 70%)
    # Same bracket structure applies 1965-1969 for single filers.
    # Medicare (HI) tax begins in 1966.
    # =========================================================================
    1965: {
        'brackets': [
            (500, 0.14),
            (1000, 0.15),
            (1500, 0.16),
            (2000, 0.17),
            (4000, 0.19),
            (6000, 0.22),
            (8000, 0.25),
            (10000, 0.28),
            (12000, 0.32),
            (14000, 0.36),
            (16000, 0.39),
            (18000, 0.42),
            (20000, 0.45),
            (22000, 0.48),
            (26000, 0.50),
            (32000, 0.53),
            (38000, 0.55),
            (44000, 0.58),
            (50000, 0.60),
            (60000, 0.62),
            (70000, 0.64),
            (80000, 0.66),
            (90000, 0.68),
            (100000, 0.69),
            (float('inf'), 0.70),
        ],
        'standard_deduction': 1000,
        'personal_exemption': 600,
        'ss_wage_base': 4800,
        'ss_rate': 0.03625,
        'medicare_rate': 0.0,
    },
    1966: {
        'brackets': [
            (500, 0.14),
            (1000, 0.15),
            (1500, 0.16),
            (2000, 0.17),
            (4000, 0.19),
            (6000, 0.22),
            (8000, 0.25),
            (10000, 0.28),
            (12000, 0.32),
            (14000, 0.36),
            (16000, 0.39),
            (18000, 0.42),
            (20000, 0.45),
            (22000, 0.48),
            (26000, 0.50),
            (32000, 0.53),
            (38000, 0.55),
            (44000, 0.58),
            (50000, 0.60),
            (60000, 0.62),
            (70000, 0.64),
            (80000, 0.66),
            (90000, 0.68),
            (100000, 0.69),
            (float('inf'), 0.70),
        ],
        'standard_deduction': 1000,
        'personal_exemption': 600,
        'ss_wage_base': 6600,
        'ss_rate': 0.0385,
        'medicare_rate': 0.0035,
    },
    1967: {
        'brackets': [
            (500, 0.14),
            (1000, 0.15),
            (1500, 0.16),
            (2000, 0.17),
            (4000, 0.19),
            (6000, 0.22),
            (8000, 0.25),
            (10000, 0.28),
            (12000, 0.32),
            (14000, 0.36),
            (16000, 0.39),
            (18000, 0.42),
            (20000, 0.45),
            (22000, 0.48),
            (26000, 0.50),
            (32000, 0.53),
            (38000, 0.55),
            (44000, 0.58),
            (50000, 0.60),
            (60000, 0.62),
            (70000, 0.64),
            (80000, 0.66),
            (90000, 0.68),
            (100000, 0.69),
            (float('inf'), 0.70),
        ],
        'standard_deduction': 1000,
        'personal_exemption': 600,
        'ss_wage_base': 6600,
        'ss_rate': 0.039,
        'medicare_rate': 0.005,
    },
    1968: {
        'brackets': [
            (500, 0.14),
            (1000, 0.15),
            (1500, 0.16),
            (2000, 0.17),
            (4000, 0.19),
            (6000, 0.22),
            (8000, 0.25),
            (10000, 0.28),
            (12000, 0.32),
            (14000, 0.36),
            (16000, 0.39),
            (18000, 0.42),
            (20000, 0.45),
            (22000, 0.48),
            (26000, 0.50),
            (32000, 0.53),
            (38000, 0.55),
            (44000, 0.58),
            (50000, 0.60),
            (60000, 0.62),
            (70000, 0.64),
            (80000, 0.66),
            (90000, 0.68),
            (100000, 0.69),
            (float('inf'), 0.70),
        ],
        'standard_deduction': 1000,
        'personal_exemption': 600,
        'ss_wage_base': 7800,
        'ss_rate': 0.038,
        'medicare_rate': 0.006,
    },
    1969: {
        'brackets': [
            (500, 0.14),
            (1000, 0.15),
            (1500, 0.16),
            (2000, 0.17),
            (4000, 0.19),
            (6000, 0.22),
            (8000, 0.25),
            (10000, 0.28),
            (12000, 0.32),
            (14000, 0.36),
            (16000, 0.39),
            (18000, 0.42),
            (20000, 0.45),
            (22000, 0.48),
            (26000, 0.50),
            (32000, 0.53),
            (38000, 0.55),
            (44000, 0.58),
            (50000, 0.60),
            (60000, 0.62),
            (70000, 0.64),
            (80000, 0.66),
            (90000, 0.68),
            (100000, 0.69),
            (float('inf'), 0.70),
        ],
        'standard_deduction': 1000,
        'personal_exemption': 600,
        'ss_wage_base': 7800,
        'ss_rate': 0.042,
        'medicare_rate': 0.006,
    },

    # =========================================================================
    # 1970-1975: Tax Reform Act of 1969 created separate single-filer schedule.
    # Brackets remain 14%-70% but with different thresholds from 1971 onward.
    # Personal exemption rises: $625 (1970), $675 (1971), $750 (1972-1978).
    # Standard deduction changes from percentage-based to flat amounts.
    # =========================================================================
    1970: {
        'brackets': [
            (500, 0.14),
            (1000, 0.15),
            (1500, 0.16),
            (2000, 0.17),
            (4000, 0.19),
            (6000, 0.21),
            (8000, 0.24),
            (10000, 0.25),
            (12000, 0.27),
            (14000, 0.29),
            (16000, 0.31),
            (18000, 0.34),
            (20000, 0.36),
            (22000, 0.38),
            (26000, 0.40),
            (32000, 0.45),
            (38000, 0.50),
            (44000, 0.55),
            (50000, 0.60),
            (60000, 0.62),
            (70000, 0.64),
            (80000, 0.66),
            (90000, 0.68),
            (100000, 0.69),
            (float('inf'), 0.70),
        ],
        'standard_deduction': 1100,
        'personal_exemption': 625,
        'ss_wage_base': 7800,
        'ss_rate': 0.042,
        'medicare_rate': 0.006,
    },
    1971: {
        'brackets': [
            (500, 0.14),
            (1000, 0.15),
            (1500, 0.16),
            (2000, 0.17),
            (4000, 0.19),
            (6000, 0.21),
            (8000, 0.24),
            (10000, 0.25),
            (12000, 0.27),
            (14000, 0.29),
            (16000, 0.31),
            (18000, 0.34),
            (20000, 0.36),
            (22000, 0.38),
            (26000, 0.40),
            (32000, 0.45),
            (38000, 0.50),
            (44000, 0.55),
            (50000, 0.60),
            (60000, 0.62),
            (70000, 0.64),
            (80000, 0.66),
            (90000, 0.68),
            (100000, 0.69),
            (float('inf'), 0.70),
        ],
        'standard_deduction': 1050,
        'personal_exemption': 675,
        'ss_wage_base': 7800,
        'ss_rate': 0.046,
        'medicare_rate': 0.006,
    },
    1972: {
        'brackets': [
            (500, 0.14),
            (1000, 0.15),
            (1500, 0.16),
            (2000, 0.17),
            (4000, 0.19),
            (6000, 0.21),
            (8000, 0.24),
            (10000, 0.25),
            (12000, 0.27),
            (14000, 0.29),
            (16000, 0.31),
            (18000, 0.34),
            (20000, 0.36),
            (22000, 0.38),
            (26000, 0.40),
            (32000, 0.45),
            (38000, 0.50),
            (44000, 0.55),
            (50000, 0.60),
            (60000, 0.62),
            (70000, 0.64),
            (80000, 0.66),
            (90000, 0.68),
            (100000, 0.69),
            (float('inf'), 0.70),
        ],
        'standard_deduction': 1300,
        'personal_exemption': 750,
        'ss_wage_base': 9000,
        'ss_rate': 0.046,
        'medicare_rate': 0.006,
    },
    1973: {
        'brackets': [
            (500, 0.14),
            (1000, 0.15),
            (1500, 0.16),
            (2000, 0.17),
            (4000, 0.19),
            (6000, 0.21),
            (8000, 0.24),
            (10000, 0.25),
            (12000, 0.27),
            (14000, 0.29),
            (16000, 0.31),
            (18000, 0.34),
            (20000, 0.36),
            (22000, 0.38),
            (26000, 0.40),
            (32000, 0.45),
            (38000, 0.50),
            (44000, 0.55),
            (50000, 0.60),
            (60000, 0.62),
            (70000, 0.64),
            (80000, 0.66),
            (90000, 0.68),
            (100000, 0.69),
            (float('inf'), 0.70),
        ],
        'standard_deduction': 1300,
        'personal_exemption': 750,
        'ss_wage_base': 10800,
        'ss_rate': 0.0485,
        'medicare_rate': 0.01,
    },
    1974: {
        'brackets': [
            (500, 0.14),
            (1000, 0.15),
            (1500, 0.16),
            (2000, 0.17),
            (4000, 0.19),
            (6000, 0.21),
            (8000, 0.24),
            (10000, 0.25),
            (12000, 0.27),
            (14000, 0.29),
            (16000, 0.31),
            (18000, 0.34),
            (20000, 0.36),
            (22000, 0.38),
            (26000, 0.40),
            (32000, 0.45),
            (38000, 0.50),
            (44000, 0.55),
            (50000, 0.60),
            (60000, 0.62),
            (70000, 0.64),
            (80000, 0.66),
            (90000, 0.68),
            (100000, 0.69),
            (float('inf'), 0.70),
        ],
        'standard_deduction': 1300,
        'personal_exemption': 750,
        'ss_wage_base': 13200,
        'ss_rate': 0.04950,
        'medicare_rate': 0.009,
    },
    1975: {
        'brackets': [
            (500, 0.14),
            (1000, 0.15),
            (1500, 0.16),
            (2000, 0.17),
            (4000, 0.19),
            (6000, 0.21),
            (8000, 0.24),
            (10000, 0.25),
            (12000, 0.27),
            (14000, 0.29),
            (16000, 0.31),
            (18000, 0.34),
            (20000, 0.36),
            (22000, 0.38),
            (26000, 0.40),
            (32000, 0.45),
            (38000, 0.50),
            (44000, 0.55),
            (50000, 0.60),
            (60000, 0.62),
            (70000, 0.64),
            (80000, 0.66),
            (90000, 0.68),
            (100000, 0.69),
            (float('inf'), 0.70),
        ],
        'standard_deduction': 1600,
        'personal_exemption': 750,
        'ss_wage_base': 14100,
        'ss_rate': 0.04950,
        'medicare_rate': 0.009,
    },

    # =========================================================================
    # 1976-1977: Tax Reform Act of 1976 introduced "zero bracket amount"
    # (standard deduction built into rate tables). Brackets start at the
    # zero-bracket threshold ($2,200 for single filers).
    # =========================================================================
    1976: {
        'brackets': [
            (500, 0.14),
            (1000, 0.15),
            (1500, 0.16),
            (2000, 0.17),
            (4000, 0.19),
            (6000, 0.21),
            (8000, 0.24),
            (10000, 0.25),
            (12000, 0.27),
            (14000, 0.29),
            (16000, 0.31),
            (18000, 0.34),
            (20000, 0.36),
            (22000, 0.38),
            (26000, 0.40),
            (32000, 0.45),
            (38000, 0.50),
            (44000, 0.55),
            (50000, 0.60),
            (60000, 0.62),
            (70000, 0.64),
            (80000, 0.66),
            (90000, 0.68),
            (100000, 0.69),
            (float('inf'), 0.70),
        ],
        'standard_deduction': 1700,
        'personal_exemption': 750,
        'ss_wage_base': 15300,
        'ss_rate': 0.04950,
        'medicare_rate': 0.009,
    },
    1977: {
        # The Tax Reform Act of 1976 introduced the "zero bracket amount"
        # ($2,200 single) built into the rate tables. The brackets below
        # have the ZBA offset removed so they apply to taxable income
        # after the standard deduction is subtracted (consistent with
        # the approach used for all other years in this file).
        'brackets': [
            (500, 0.14),
            (1000, 0.15),
            (1500, 0.16),
            (2000, 0.17),
            (4000, 0.19),
            (6000, 0.21),
            (8000, 0.24),
            (10000, 0.25),
            (12000, 0.27),
            (14000, 0.29),
            (16000, 0.31),
            (18000, 0.34),
            (20000, 0.36),
            (22000, 0.38),
            (26000, 0.40),
            (32000, 0.45),
            (38000, 0.50),
            (44000, 0.55),
            (50000, 0.60),
            (60000, 0.62),
            (70000, 0.64),
            (80000, 0.66),
            (90000, 0.68),
            (100000, 0.69),
            (float('inf'), 0.70),
        ],
        'standard_deduction': 2200,
        'personal_exemption': 750,
        'ss_wage_base': 16500,
        'ss_rate': 0.04950,
        'medicare_rate': 0.009,
    },

    # =========================================================================
    # 1978-1981: Revenue Act of 1978 restructured brackets.
    # Zero bracket amount ($2,300 single) built into tables 1979+.
    # Personal exemption: $750 (1978), $1,000 (1979-1984).
    # ERTA 1981 began phased rate reductions.
    # =========================================================================
    1978: {
        # Revenue Act of 1978 restructured brackets. ZBA of $2,300 removed
        # from thresholds below (brackets apply to taxable income after
        # standard deduction and personal exemption are subtracted).
        'brackets': [
            (1100, 0.14),
            (2100, 0.16),
            (4200, 0.18),
            (6200, 0.19),
            (8500, 0.21),
            (10600, 0.24),
            (12700, 0.26),
            (15900, 0.30),
            (21200, 0.34),
            (26500, 0.39),
            (31800, 0.44),
            (39200, 0.49),
            (53000, 0.55),
            (79500, 0.63),
            (106000, 0.68),
            (float('inf'), 0.70),
        ],
        'standard_deduction': 2300,
        'personal_exemption': 750,
        'ss_wage_base': 17700,
        'ss_rate': 0.05050,
        'medicare_rate': 0.01,
    },
    1979: {
        'brackets': [
            (1100, 0.14),
            (2100, 0.16),
            (4200, 0.18),
            (6200, 0.19),
            (8500, 0.21),
            (10600, 0.24),
            (12700, 0.26),
            (15900, 0.30),
            (21200, 0.34),
            (26500, 0.39),
            (31800, 0.44),
            (39200, 0.49),
            (53000, 0.55),
            (79500, 0.63),
            (106000, 0.68),
            (float('inf'), 0.70),
        ],
        'standard_deduction': 2300,
        'personal_exemption': 1000,
        'ss_wage_base': 22900,
        'ss_rate': 0.05080,
        'medicare_rate': 0.0105,
    },
    1980: {
        'brackets': [
            (1100, 0.14),
            (2100, 0.16),
            (4200, 0.18),
            (6200, 0.19),
            (8500, 0.21),
            (10600, 0.24),
            (12700, 0.26),
            (15900, 0.30),
            (21200, 0.34),
            (26500, 0.39),
            (31800, 0.44),
            (39200, 0.49),
            (53000, 0.55),
            (79500, 0.63),
            (106000, 0.68),
            (float('inf'), 0.70),
        ],
        'standard_deduction': 2300,
        'personal_exemption': 1000,
        'ss_wage_base': 25900,
        'ss_rate': 0.05080,
        'medicare_rate': 0.0105,
    },
    1981: {
        # ERTA 1981 began phased rate reductions. First year: top rate
        # reduced from 70% to 50%.
        'brackets': [
            (1100, 0.12),
            (2100, 0.14),
            (4200, 0.16),
            (6200, 0.17),
            (8500, 0.19),
            (10600, 0.22),
            (12700, 0.23),
            (15900, 0.27),
            (21200, 0.31),
            (26500, 0.35),
            (31800, 0.40),
            (39200, 0.44),
            (float('inf'), 0.50),
        ],
        'standard_deduction': 2300,
        'personal_exemption': 1000,
        'ss_wage_base': 29700,
        'ss_rate': 0.05350,
        'medicare_rate': 0.013,
    },

    # =========================================================================
    # 1982-1986: ERTA phased-in rate reductions.
    # 1982-1983: Rates cut ~10% each year from 1981 levels.
    # 1984: Indexing of brackets for inflation begins.
    # Personal exemption: $1,000 (1982-1984), $1,040 (1985), $1,080 (1986).
    # =========================================================================
    1982: {
        'brackets': [
            (1100, 0.11),
            (2100, 0.13),
            (6200, 0.15),
            (8500, 0.17),
            (10600, 0.19),
            (12700, 0.21),
            (15900, 0.24),
            (21200, 0.28),
            (26500, 0.32),
            (31800, 0.36),
            (39200, 0.40),
            (53000, 0.45),
            (float('inf'), 0.50),
        ],
        'standard_deduction': 2300,
        'personal_exemption': 1000,
        'ss_wage_base': 32400,
        'ss_rate': 0.05400,
        'medicare_rate': 0.013,
    },
    1983: {
        'brackets': [
            (1100, 0.11),
            (2100, 0.12),
            (4200, 0.14),
            (6200, 0.15),
            (8500, 0.16),
            (10600, 0.18),
            (12700, 0.20),
            (15900, 0.23),
            (21200, 0.26),
            (26500, 0.30),
            (31800, 0.34),
            (39200, 0.38),
            (53000, 0.42),
            (79500, 0.48),
            (float('inf'), 0.50),
        ],
        'standard_deduction': 2300,
        'personal_exemption': 1000,
        'ss_wage_base': 35700,
        'ss_rate': 0.05400,
        'medicare_rate': 0.013,
    },
    1984: {
        # Bracket indexing for inflation begins in 1984.
        # ZBA of $2,390 removed from thresholds.
        'brackets': [
            (1150, 0.11),
            (2190, 0.12),
            (4370, 0.14),
            (6460, 0.15),
            (8850, 0.16),
            (11040, 0.18),
            (13220, 0.20),
            (16550, 0.23),
            (22070, 0.26),
            (27580, 0.30),
            (33100, 0.34),
            (40800, 0.38),
            (55160, 0.42),
            (82740, 0.48),
            (float('inf'), 0.50),
        ],
        'standard_deduction': 2390,
        'personal_exemption': 1000,
        'ss_wage_base': 37800,
        'ss_rate': 0.05700,
        'medicare_rate': 0.013,
    },
    1985: {
        # ZBA of $2,480 removed from thresholds.
        'brackets': [
            (1190, 0.11),
            (2270, 0.12),
            (4530, 0.14),
            (6690, 0.15),
            (9170, 0.16),
            (11440, 0.18),
            (13710, 0.20),
            (17160, 0.23),
            (22880, 0.26),
            (28600, 0.30),
            (34320, 0.34),
            (42300, 0.38),
            (57190, 0.42),
            (85790, 0.48),
            (float('inf'), 0.50),
        ],
        'standard_deduction': 2480,
        'personal_exemption': 1040,
        'ss_wage_base': 39600,
        'ss_rate': 0.05700,
        'medicare_rate': 0.0135,
    },
    1986: {
        # 1986 brackets follow the same ERTA structure as 1985, indexed for
        # inflation. ZBA of $2,560 removed from thresholds.
        # Source: IRS Revenue Procedure 85-47 / IRS Publication 17 (1986).
        'brackets': [
            (1230, 0.11),
            (2340, 0.12),
            (4680, 0.14),
            (6910, 0.15),
            (9460, 0.16),
            (11820, 0.18),
            (14160, 0.20),
            (17710, 0.23),
            (23610, 0.26),
            (29510, 0.30),
            (35420, 0.34),
            (43650, 0.38),
            (59000, 0.42),
            (88540, 0.48),
            (float('inf'), 0.50),
        ],
        'standard_deduction': 2560,
        'personal_exemption': 1080,
        'ss_wage_base': 42000,
        'ss_rate': 0.0570,
        'medicare_rate': 0.0145,
    },

    # =========================================================================
    # 1987: Tax Reform Act of 1986 takes effect. Simplified to 2 brackets
    # (15% and 28%) plus a "bubble" rate (33%) that phased out the benefit
    # of the lower bracket and personal exemption for high earners.
    # =========================================================================
    1987: {
        'brackets': [
            (17850, 0.15),
            (float('inf'), 0.28),
        ],
        'standard_deduction': 2540,
        'personal_exemption': 1900,
        'ss_wage_base': 43800,
        'ss_rate': 0.0570,
        'medicare_rate': 0.0145,
    },

    # =========================================================================
    # 1988-1990: Two-bracket system (15%/28%).
    # 1990: OBRA 1990 added 31% bracket.
    # Personal exemption indexed: $1,950 (1988), $2,000 (1989), $2,050 (1990).
    # Standard deduction rises: $3,000 (1988), $3,100 (1989), $3,250 (1990).
    # =========================================================================
    1988: {
        'brackets': [
            (18550, 0.15),
            (float('inf'), 0.28),
        ],
        'standard_deduction': 3000,
        'personal_exemption': 1950,
        'ss_wage_base': 45000,
        'ss_rate': 0.0606,
        'medicare_rate': 0.0145,
    },
    1989: {
        'brackets': [
            (19450, 0.15),
            (float('inf'), 0.28),
        ],
        'standard_deduction': 3100,
        'personal_exemption': 2000,
        'ss_wage_base': 48000,
        'ss_rate': 0.0606,
        'medicare_rate': 0.0145,
    },
    1990: {
        'brackets': [
            (20350, 0.15),
            (49300, 0.28),
            (float('inf'), 0.31),
        ],
        'standard_deduction': 3250,
        'personal_exemption': 2050,
        'ss_wage_base': 51300,
        'ss_rate': 0.0620,
        'medicare_rate': 0.0145,
    },

    # =========================================================================
    # 1991-1992: Three brackets (15%/28%/31%).
    # =========================================================================
    1991: {
        'brackets': [
            (21450, 0.15),
            (51900, 0.28),
            (float('inf'), 0.31),
        ],
        'standard_deduction': 3400,
        'personal_exemption': 2150,
        'ss_wage_base': 53400,
        'ss_rate': 0.0620,
        'medicare_rate': 0.0145,
    },
    1992: {
        'brackets': [
            (22100, 0.15),
            (53500, 0.28),
            (float('inf'), 0.31),
        ],
        'standard_deduction': 3600,
        'personal_exemption': 2300,
        'ss_wage_base': 55500,
        'ss_rate': 0.0620,
        'medicare_rate': 0.0145,
    },

    # =========================================================================
    # 1993-1994: OBRA 1993 added 36% and 39.6% brackets retroactively for 1993.
    # In 1994, the Medicare (HI) wage base cap was removed (unlimited).
    # =========================================================================
    1993: {
        'brackets': [
            (22750, 0.15),
            (55100, 0.28),
            (115000, 0.31),
            (250000, 0.36),
            (float('inf'), 0.396),
        ],
        'standard_deduction': 3700,
        'personal_exemption': 2350,
        'ss_wage_base': 57600,
        'ss_rate': 0.0620,
        'medicare_rate': 0.0145,
    },
    1994: {
        'brackets': [
            (23350, 0.15),
            (56550, 0.28),
            (117950, 0.31),
            (256500, 0.36),
            (float('inf'), 0.396),
        ],
        'standard_deduction': 3800,
        'personal_exemption': 2450,
        'ss_wage_base': 60600,
        'ss_rate': 0.0620,
        'medicare_rate': 0.0145,
    },
}


def calculate_federal_income_tax(taxable_income, year):
    """
    Calculate federal income tax for a single filer given taxable income and year.

    For years with a zero-bracket amount (1978-1986), the brackets already
    include the zero-bracket threshold. Taxable income should be computed as:
        taxable_income = gross_income - (adjustments + itemized_or_standard_deduction + personal_exemption)

    For years 1978-1986 where the zero bracket amount is built into the tables,
    the first bracket at rate 0.0 handles the built-in deduction.

    Args:
        taxable_income: Taxable income in dollars (after deductions and exemptions).
        year: Tax year (1961-1994).

    Returns:
        Federal income tax owed in dollars.
    """
    if year not in TAX_DATA:
        raise ValueError(f"Tax data not available for year {year}")

    brackets = TAX_DATA[year]['brackets']
    tax = 0.0
    prev_threshold = 0

    for upper_bound, rate in brackets:
        if taxable_income <= prev_threshold:
            break
        taxable_in_bracket = min(taxable_income, upper_bound) - prev_threshold
        tax += taxable_in_bracket * rate
        prev_threshold = upper_bound

    return tax


def calculate_fica(gross_wages, year):
    """
    Calculate employee FICA taxes (Social Security + Medicare) for a given year.

    For years before 1994, both SS and Medicare had the same wage base cap.
    Starting in 1994, the Medicare wage base was removed (unlimited).

    Args:
        gross_wages: Total gross wages in dollars.
        year: Tax year (1961-1994).

    Returns:
        Tuple of (social_security_tax, medicare_tax, total_fica).
    """
    if year not in TAX_DATA:
        raise ValueError(f"Tax data not available for year {year}")

    data = TAX_DATA[year]
    ss_wages = min(gross_wages, data['ss_wage_base'])
    ss_tax = ss_wages * data['ss_rate']

    # Before 1994, Medicare had the same wage base as Social Security.
    # Starting 1994, Medicare applies to all wages (no cap).
    if year >= 1994:
        medicare_wages = gross_wages
    else:
        medicare_wages = min(gross_wages, data['ss_wage_base'])

    medicare_tax = medicare_wages * data['medicare_rate']

    return ss_tax, medicare_tax, ss_tax + medicare_tax


def calculate_total_tax(gross_income, year):
    """
    Calculate total federal tax burden (income tax + FICA) for a single filer.

    Uses standard deduction and personal exemption. Does not account for
    itemized deductions, credits, or other adjustments.

    Args:
        gross_income: Total gross income in dollars.
        year: Tax year (1961-1994).

    Returns:
        Dictionary with tax breakdown.
    """
    if year not in TAX_DATA:
        raise ValueError(f"Tax data not available for year {year}")

    data = TAX_DATA[year]

    # Calculate taxable income
    deductions = data['standard_deduction'] + data['personal_exemption']
    taxable_income = max(0, gross_income - deductions)

    # Federal income tax
    income_tax = calculate_federal_income_tax(taxable_income, year)

    # FICA (applies to gross wages, not reduced by deductions)
    ss_tax, medicare_tax, total_fica = calculate_fica(gross_income, year)

    total_tax = income_tax + total_fica

    return {
        'gross_income': gross_income,
        'standard_deduction': data['standard_deduction'],
        'personal_exemption': data['personal_exemption'],
        'taxable_income': taxable_income,
        'income_tax': round(income_tax, 2),
        'ss_tax': round(ss_tax, 2),
        'medicare_tax': round(medicare_tax, 2),
        'total_fica': round(total_fica, 2),
        'total_tax': round(total_tax, 2),
        'effective_rate': round(total_tax / gross_income, 4) if gross_income > 0 else 0,
    }


if __name__ == '__main__':
    # Example: calculate taxes for $50,000 income across selected years
    test_income = 50000
    print(f"Tax calculations for ${test_income:,.0f} gross income (single filer)\n")
    print(f"{'Year':>4}  {'Std Ded':>8}  {'Pers Ex':>8}  {'Taxable':>10}  "
          f"{'Inc Tax':>10}  {'SS Tax':>8}  {'Med Tax':>8}  "
          f"{'Total Tax':>10}  {'Eff Rate':>8}")
    print("-" * 100)

    for year in sorted(TAX_DATA.keys()):
        result = calculate_total_tax(test_income, year)
        print(f"{year:>4}  "
              f"${result['standard_deduction']:>7,.0f}  "
              f"${result['personal_exemption']:>7,.0f}  "
              f"${result['taxable_income']:>9,.0f}  "
              f"${result['income_tax']:>9,.2f}  "
              f"${result['ss_tax']:>7,.2f}  "
              f"${result['medicare_tax']:>7,.2f}  "
              f"${result['total_tax']:>9,.2f}  "
              f"{result['effective_rate']:>7.2%}")
