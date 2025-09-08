"""Scan pipeline/data CSVs for price_overview and produce per-currency diagnostics."""
import os
import sys
import json
import glob
import pandas as pd
from collections import defaultdict

# Ensure pipeline/src is importable so we can use the canonical PriceOverview logic
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
src_path = os.path.join(repo_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from ags_pipeline.models.steam_models import PriceOverview

data_dir = os.path.join(repo_root, 'data')


def probe_csv(path, sample_limit_per_note=5):
    try:
        df = pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return {}
    stats = {}
    for _, row in df.iterrows():
        po = None
        if 'price_overview' in row:
            po = row['price_overview']
        if pd.isna(po):
            continue
        # try parse stringified JSON
        if isinstance(po, str):
            try:
                po = json.loads(po)
            except Exception:
                # keep as-is
                pass
        if not isinstance(po, dict):
            continue

        # Use PriceOverview.from_dict for canonical normalization and note
        p = PriceOverview.from_dict(po)
        currency = (p.currency or 'UNKNOWN').upper()
        note = p.normalization_note or 'unknown'

        s = stats.setdefault(currency, {
            'total': 0,
            'by_note': defaultdict(int),
            'note_examples': defaultdict(list),
            'values_sample': []
        })
        s['total'] += 1
        s['by_note'][note] += 1
        # store small samples per note
        if len(s['note_examples'][note]) < sample_limit_per_note:
            s['note_examples'][note].append({'raw_final': p.raw_final, 'normalized': p.final})
        if p.final is not None and len(s['values_sample']) < 50:
            s['values_sample'].append(p.final)

    # finalize stats: convert defaultdicts to dicts and compute fractions
    out = {}
    for cur, v in stats.items():
        by_note = dict(v['by_note'])
        assumed_count = 0
        for kname, cnt in by_note.items():
            if 'assumed' in kname or 'assume' in kname:
                assumed_count += cnt
        frac_assumed = assumed_count / v['total'] if v['total'] else 0.0
        out[cur] = {
            'total': v['total'],
            'by_note': by_note,
            'note_examples': {k: list(es) for k, es in v['note_examples'].items()},
            'values_sample': v['values_sample'],
            'fraction_assumed': frac_assumed
        }
    return out


def main(assume_threshold=0.05):
    out = {}
    warnings = []
    for csv in glob.glob(os.path.join(data_dir, '*.csv')):
        name = os.path.basename(csv)
        s = probe_csv(csv)
        out[name] = s
        # check for currencies exceeding assumption threshold
        for cur, v in s.items():
            if v.get('fraction_assumed', 0) > assume_threshold:
                warnings.append({'file': name, 'currency': cur, 'fraction_assumed': v['fraction_assumed']})

    report = {'files': out, 'warnings': warnings}
    out_path = os.path.join(data_dir, 'price_probe.json')
    with open(out_path, 'w', encoding='utf8') as f:
        json.dump(report, f, indent=2)
    print('Wrote', out_path)
    if warnings:
        print('Warnings: currencies with high assumed normalization fraction:')
        for w in warnings:
            print(w)


if __name__ == '__main__':
    main()
