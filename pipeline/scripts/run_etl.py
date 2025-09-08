"""ETL Runner

Steps:
- Join price_minmax.json into flattened app artifacts (expanded_sampled_apps.*)
- Replace originals in-place with timestamped backups
- Load the updated artifacts into SQLite via etl_to_sqlite
"""
from __future__ import annotations
import datetime
from pathlib import Path
import importlib
from importlib.util import spec_from_file_location, module_from_spec
import sys

import pandas as pd

from ags_pipeline.io.price_minmax_loader import load_price_minmax, join_price_minmax


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'


def _backup(p: Path):
    if p.exists():
        ts = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        bak = p.with_suffix(p.suffix + f'.bak.{ts}')
        p.replace(bak)
        print(f'Backup: {p.name} -> {bak.name}')


def join_and_replace():
    csvp = DATA / 'expanded_sampled_apps.csv'
    feap = DATA / 'expanded_sampled_apps.feather'

    # load input
    if feap.exists():
        try:
            df = pd.read_feather(feap)
            print(f'Loaded feather: {feap}')
        except Exception as e:
            print(f'Feather load failed ({e}); falling back to CSV')
            df = pd.read_csv(csvp, low_memory=False)
    else:
        df = pd.read_csv(csvp, low_memory=False)
        print(f'Loaded csv: {csvp}')

    pm = load_price_minmax()
    appid_col = 'steam_appid' if 'steam_appid' in df.columns else 'appid'
    jdf = join_price_minmax(df, pm, appid_col=appid_col)

    # replace originals with backups
    _backup(csvp)
    _backup(feap)
    jdf.to_csv(csvp, index=False)
    print(f'Wrote updated CSV with min/max: {csvp}')
    try:
        jdf.to_feather(feap)
        print(f'Wrote updated Feather with min/max: {feap}')
    except Exception as e:
        print(f'Feather write failed: {e}')


def load_sqlite():
    # Import and run existing SQLite ETL
    spec = spec_from_file_location('etl_to_sqlite', ROOT / 'scripts' / 'etl_to_sqlite.py')
    if not spec or not spec.loader:
        raise RuntimeError('Failed to locate etl_to_sqlite.py')
    mod = module_from_spec(spec)
    sys.modules['etl_to_sqlite'] = mod
    spec.loader.exec_module(mod)
    if hasattr(mod, 'main'):
        mod.main()
    else:
        raise RuntimeError('etl_to_sqlite.py missing main()')


def main():
    join_and_replace()
    load_sqlite()


if __name__ == '__main__':
    main()
