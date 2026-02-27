import csv
from collections import Counter

usable = Counter()
total = Counter()

with open('cps_00003.csv') as f:
    r = csv.DictReader(f)
    for row in r:
        yr = row['YEAR']
        total[yr] += 1
        wt = row.get('ASECWT', '')
        inc = row.get('INCTOT', '')
        if wt and wt != '0' and inc and inc not in ('999999999', '99999999'):
            usable[yr] += 1

for yr in sorted(usable.keys()):
    pct = usable[yr] / total[yr] * 100
    print(f'{yr}: {usable[yr]:>8} usable / {total[yr]:>8} total ({pct:.1f}%)')
