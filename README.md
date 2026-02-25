# U.S. Income by Age & Percentile — Complete Pipeline

## What This Is

A pipeline that computes **individual income percentiles by single year of age**
for every year from 1995–2025, using the authoritative source: Census Bureau CPS
ASEC microdata via IPUMS-CPS.

This is the same data source DQYDJ.com uses. The difference is you'll have the
raw microdata and full control over the computation, not scraped summary tables.

## Architecture

```
IPUMS-CPS (download) → cps_asec.csv.gz
        ↓
process_income.py (weighted percentile computation)
        ↓
income_percentiles.json (structured output)
        ↓
income_explorer.jsx (React visualization)
```

---

## Step 1: Get the Data from IPUMS-CPS

This is the only manual step. It takes about 10 minutes.

### 1a. Create a free account

Go to **https://cps.ipums.org** and register. It's free. Academic or personal
use is fine. They ask for a brief description of your project — "personal
research on income distribution trends" is sufficient.

### 1b. Create a data extract

1. Go to **https://cps.ipums.org/cps-action/data_requests/download**
2. Click **"Create New Extract"**
3. **Select Samples**: Click "Select Samples" → check **ASEC** samples for every
   year you want. For 1995–2025, that's the ASEC supplement for each March survey
   from 1996 (which covers income year 1995) through 2025 (income year 2024).
   - The ASEC sample is listed as "ASEC" next to each year
   - You can use "Select All" and then uncheck non-ASEC months
4. **Select Variables**: Search for and add these variables to your cart:
   - `AGE` — Age of respondent
   - `INCTOT` — Total personal income (all sources)
   - `ASECWT` — ASEC supplement weight (CRITICAL — this makes it representative)
   - `YEAR` — Survey year (auto-included)
   - `WKSTAT` — Full/part-time work status (optional, for filtering)
   - `EMPSTAT` — Employment status (optional, for worker screen)
5. **Data Format**: Select **CSV** (comma-delimited) with the option for a
   **rectangular** file structure (one row per person).
6. **Submit Extract** and wait for the email notification (usually 5–30 minutes
   depending on size).

### 1c. Download and place the file

Download the `.csv.gz` file. Place it in this project directory as:

```
cps_asec.csv.gz
```

The file will be roughly 500MB–1.5GB compressed depending on how many years and
variables you selected.

---

## Step 2: Run the Processing Script

### Requirements

```bash
pip install pandas numpy
```

### Run

```bash
python process_income.py
```

This will:
1. Read the IPUMS CSV extract
2. Apply the DQYDJ-style worker screen (people who worked or wanted to work)
3. For each year × age combination, compute weighted percentiles
   (1st, 5th, 10th, 25th, 50th, 75th, 90th, 95th, 99th)
   plus weighted mean and sample count
4. Output `income_percentiles.json` — a structured file the visualization reads

Runtime: ~2–5 minutes depending on your machine and the number of years.

---

## Step 3: Visualize

Copy `income_percentiles.json` into the same directory as the React component,
or paste its contents into the data constant in `income_explorer.jsx`.

The visualization provides:
- Age-profile view (x = age, y = income, one line per percentile)
- Time-series view (x = year, y = income for a selected age)
- CPI inflation adjustment toggle
- Year comparison (solid vs dashed lines)
- Full data table export

---

## Data Notes

- **Income definition**: INCTOT = total personal income from all sources
  (wages, business, investments, interest, transfers, etc.)
- **Worker screen**: Following DQYDJ methodology, the default filter includes
  people who were employed or actively looking for work (EMPSTAT in [10, 12, 20, 21, 22]).
  You can toggle this in the script.
- **Weights**: ASECWT must be used. Without weights, the data is not
  representative of the U.S. population.
- **Top-coding**: The Census top-codes very high incomes. This means the 99th
  percentile and above may be understated compared to tax data (IRS SOI).
  The top-code threshold has changed over time.
- **Age perturbation**: For ASEC years 2003–2010, the Census Bureau applied age
  perturbation to public-use files that slightly distorts data for ages 65+.
  This primarily affects the elderly; ages 18–64 are minimally impacted.
