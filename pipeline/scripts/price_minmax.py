"""Compute per-app min/max normalized prices across pipeline/data CSV snapshots.

Produces pipeline/data/price_minmax.json with structure { appid: {min, max, samples, count} }
"""
import os
import sys
import glob
import json
import pandas as pd

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
src_path = os.path.join(repo_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from ags_pipeline.models.steam_models import PriceOverview

data_dir = os.path.join(repo_root, 'data')


def extract_appid(row):
    for k in ('steam_appid','appid','app_id','id'):
        if k in row and pd.notna(row[k]):
            try:
                return int(row[k])
            except Exception:
                return row[k]
    return None


def parse_priceobj(val):
    # val may be dict or JSON string
    if pd.isna(val):
        return None
    if isinstance(val, str):
        try:
            import json as _json
            return _json.loads(val)
        except Exception:
            return None
    if isinstance(val, dict):
        return val
    return None


def main():
    apps = {}
    csvs = glob.glob(os.path.join(data_dir, '*.csv'))
    for path in csvs:
        try:
            df = pd.read_csv(path)
        except pd.errors.EmptyDataError:
            continue
        for _, row in df.iterrows():
            appid = extract_appid(row)
            if appid is None:
                continue
            po = None
            if 'price_overview' in row:
                po = parse_priceobj(row['price_overview'])
            if not isinstance(po, dict):
                continue
            p = PriceOverview.from_dict(po)
            if p is None or p.final is None:
                continue
            rec = apps.setdefault(str(appid), {'min': None, 'max': None, 'samples': [], 'count': 0})
            v = p.final
            if rec['min'] is None or v < rec['min']:
                rec['min'] = v
            if rec['max'] is None or v > rec['max']:
                rec['max'] = v
            if len(rec['samples']) < 5:
                rec['samples'].append({'raw': p.raw_final, 'normalized': p.final, 'note': p.normalization_note})
            rec['count'] += 1

    out_path = os.path.join(data_dir, 'price_minmax.json')
    with open(out_path, 'w', encoding='utf8') as f:
        json.dump(apps, f, indent=2)

    # Print a short summary
    totals = len(apps)
    with_minmax = sum(1 for v in apps.values() if v['min'] is not None and v['max'] is not None)
    print(f'Wrote {out_path}; apps with price samples: {totals}; with min/max: {with_minmax}')


if __name__ == '__main__':
    main()
