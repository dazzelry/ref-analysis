import csv
from datetime import datetime
from pathlib import Path

data_dir = Path('data')
source_files = ['all_games.csv', '22_23.csv', '23_24.csv', '24_25.csv', '25_26.csv']
out_file = data_dir / 'total_games.csv'
header = ['home_team', 'away_team', 'date', 'referee', 'home_fouls', 'away_fouls', 'home_yellow', 'away_yellow', 'total_fouls', 'total_yellows']


def norm_key(k):
    return k.strip().lower() if k else ''


def parse_date(value):
    if not value:
        return ''
    value = value.strip().strip('"')
    if ',' in value and any(month in value for month in ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']):
        return value
    for fmt in ['%d/%m/%Y', '%d/%m/%y', '%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y']:
        try:
            dt = datetime.strptime(value, fmt)
            return f"{dt.strftime('%A')} {dt.strftime('%B')} {dt.day}, {dt.year}"
        except ValueError:
            continue
    return value


def to_int(value):
    try:
        return int(float(value))
    except Exception:
        return None


def first_existing(row, keys):
    for k in keys:
        if k in row and row[k] != '':
            return row[k]
    return ''


rows = []
for fname in source_files:
    path = data_dir / fname
    if not path.exists():
        raise FileNotFoundError(f"Missing source file: {path}")
    with path.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for raw in reader:
            row = {norm_key(k): (v or '').strip() for k, v in raw.items()}
            out = {
                'home_team': first_existing(row, ['hometeam', 'home_team', 'home team', 'home']),
                'away_team': first_existing(row, ['awayteam', 'away_team', 'away team', 'away']),
                'date': parse_date(first_existing(row, ['date', 'matchdate', 'day', 'datetime', 'date_time'])),
                'referee': first_existing(row, ['referee', 'ref']),
            }
            hf = to_int(first_existing(row, ['home_fouls', 'hf', 'homefouls', 'home_foul', 'hfoul', 'home']))
            af = to_int(first_existing(row, ['away_fouls', 'af', 'awayfouls', 'away_foul', 'afoul', 'away']))
            hy = to_int(first_existing(row, ['home_yellow', 'hy', 'homeyellow', 'home_yellows', 'hyellow']))
            ay = to_int(first_existing(row, ['away_yellow', 'ay', 'awayyellow', 'away_yellows', 'ayellow']))
            total_f = first_existing(row, ['total_fouls', 'tf', 'totalfouls', 'total_foul', 'totalf'])
            total_y = first_existing(row, ['total_yellows', 'ty', 'totalyellows', 'total_yellow', 'totaly'])
            if total_f == '' and hf is not None and af is not None:
                total_f = str(hf + af)
            if total_y == '' and hy is not None and ay is not None:
                total_y = str(hy + ay)
            out['home_fouls'] = str(hf) if hf is not None else first_existing(row, ['home_fouls', 'hf', 'homefouls', 'home_foul', 'home'])
            out['away_fouls'] = str(af) if af is not None else first_existing(row, ['away_fouls', 'af', 'awayfouls', 'away_foul', 'away'])
            out['home_yellow'] = str(hy) if hy is not None else first_existing(row, ['home_yellow', 'hy', 'homeyellow', 'home_yellows', 'hyellow'])
            out['away_yellow'] = str(ay) if ay is not None else first_existing(row, ['away_yellow', 'ay', 'awayyellow', 'away_yellows', 'ayellow'])
            out['total_fouls'] = total_f
            out['total_yellows'] = total_y
            rows.append(out)

with out_file.open('w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=header)
    writer.writeheader()
    writer.writerows(rows)

print(f'Wrote {len(rows)} rows to {out_file}')
