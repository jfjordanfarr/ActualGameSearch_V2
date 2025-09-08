from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any, Optional

import pandas as pd


def _resolve_default_path() -> Path:
    # default data path relative to repository root
    # file is at pipeline/src/ags_pipeline/io -> parents[4] is repository root
    repo_root = Path(__file__).resolve().parents[4]
    return repo_root / 'pipeline' / 'data' / 'price_minmax.json'


def load_price_minmax(path: Optional[str | Path] = None) -> Dict[int, Dict[str, Any]]:
    """Load price_minmax.json and return a mapping of appid (int) -> record.

    The returned record typically contains keys like 'min', 'max', 'count', and
    'samples'. AppIDs are converted to int when possible for easy joining.
    """
    p = Path(path) if path else _resolve_default_path()
    if not p.exists():
        raise FileNotFoundError(f"price_minmax file not found: {p}")
    raw = json.loads(p.read_text(encoding='utf-8'))
    out: Dict[int, Dict[str, Any]] = {}
    # Expect structure { 'apps': { '<appid>': {...}, ... } } or a flat dict
    apps = raw.get('apps') if isinstance(raw, dict) and 'apps' in raw else raw
    if not isinstance(apps, dict):
        raise ValueError('unexpected price_minmax.json layout')

    for k, v in apps.items():
        try:
            aik = int(k)
        except Exception:
            # fallback: try stripping and converting
            try:
                aik = int(str(k).strip())
            except Exception:
                # skip non-int keys
                continue
        out[aik] = v if isinstance(v, dict) else {'value': v}
    return out


def join_price_minmax(df: pd.DataFrame, price_minmax: Dict[int, Dict[str, Any]], appid_col: str = 'appid') -> pd.DataFrame:
    """Return a copy of df with columns added: price_min, price_max, price_samples_count.

    If an appid is missing in `price_minmax`, the added columns will be NaN/0.
    """
    if appid_col not in df.columns:
        raise KeyError(f"appid column '{appid_col}' not found in DataFrame")
    df2 = df.copy()
    # build series by mapping appid -> min/max/count
    def _map_field(col_name: str):
        return df2[appid_col].map(lambda x: (price_minmax.get(int(x)) if pd.notna(x) and str(x).strip().isdigit() else None)).map(lambda rec: rec.get(col_name) if rec and col_name in rec else None)

    df2['price_min'] = _map_field('min')
    df2['price_max'] = _map_field('max')
    # count of samples (may be under 'count' or len(samples))
    def _map_count(x):
        rec = price_minmax.get(int(x)) if pd.notna(x) and str(x).strip().isdigit() else None
        if not rec:
            return 0
        if 'count' in rec and isinstance(rec['count'], int):
            return rec['count']
        samples = rec.get('samples') or rec.get('values') or []
        try:
            return int(len(samples))
        except Exception:
            return 0

    df2['price_samples_count'] = df2[appid_col].map(_map_count)
    return df2
