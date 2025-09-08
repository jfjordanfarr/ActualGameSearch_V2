"""Join price_minmax.json into flattened app artifacts (CSV/Feather).

This script is intentionally non-invasive: it reads the existing flattened apps
CSV/Feather (defaults to expanded_sampled_apps.csv/feather), joins price_minmax
fields (min/max/count) and writes new files with a .joined suffix and creates
timestamped backups of existing feather files when present.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import datetime
import pandas as pd

from ags_pipeline.io.price_minmax_loader import load_price_minmax, join_price_minmax


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'


def _backup_if_exists(p: Path):
    if p.exists():
        ts = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        bak = p.with_suffix(p.suffix + f'.bak.{ts}')
        p.replace(bak)
        print(f'Backed up {p} -> {bak}')


def main(input_csv=None, input_feather=None):
    csvp = Path(input_csv) if input_csv else DATA / 'expanded_sampled_apps.csv'
    feap = Path(input_feather) if input_feather else DATA / 'expanded_sampled_apps.feather'

    # load price_minmax
    pm = load_price_minmax()

    # prefer feather for speed
    if feap.exists():
        try:
            df = pd.read_feather(feap)
            print(f'Loaded apps from feather: {feap}')
        except Exception as e:
            print(f'Failed reading feather {feap}: {e}; falling back to CSV')
            df = pd.read_csv(csvp, low_memory=False)
    elif csvp.exists():
        df = pd.read_csv(csvp, low_memory=False)
        print(f'Loaded apps from csv: {csvp}')
    else:
        raise FileNotFoundError('No input app artifact found')

    joined = join_price_minmax(df, pm, appid_col='steam_appid' if 'steam_appid' in df.columns else 'appid')

    # write joined outputs
    out_csv = DATA / 'expanded_sampled_apps.joined.csv'
    out_feather = DATA / 'expanded_sampled_apps.joined.feather'

    joined.to_csv(out_csv, index=False)
    print(f'Wrote joined CSV: {out_csv}')

    # backup existing feather and write new one
    if out_feather.exists():
        _backup_if_exists(out_feather)
    try:
        joined.to_feather(out_feather)
        print(f'Wrote joined Feather: {out_feather}')
    except Exception as e:
        print(f'Failed to write feather {out_feather}: {e}')


if __name__ == '__main__':
    main()
