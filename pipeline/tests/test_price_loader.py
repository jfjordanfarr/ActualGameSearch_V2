import json
from pathlib import Path

import pandas as pd

from ags_pipeline.io.price_minmax_loader import load_price_minmax, join_price_minmax


def test_load_price_minmax(tmp_path: Path):
    data = {'apps': {'123': {'min': 1.99, 'max': 4.99, 'count': 3, 'samples': [1.99, 2.99, 4.99]},
                     '456': {'min': 0.0, 'max': 0.0, 'count': 1, 'samples': [0.0]}}}
    p = tmp_path / 'price_minmax.json'
    p.write_text(json.dumps(data), encoding='utf-8')
    out = load_price_minmax(str(p))
    assert 123 in out and 456 in out
    assert out[123]['min'] == 1.99


def test_join_price_minmax(tmp_path: Path):
    data = {'apps': {'123': {'min': 1.99, 'max': 4.99, 'count': 3, 'samples': [1.99, 2.99, 4.99]},
                     '789': {'min': 5.0, 'max': 5.0, 'count': 1, 'samples': [5.0]}}}
    p = tmp_path / 'price_minmax.json'
    p.write_text(json.dumps(data), encoding='utf-8')
    pm = load_price_minmax(str(p))
    df = pd.DataFrame([{'appid': 123, 'name': 'A'}, {'appid': 789, 'name': 'B'}, {'appid': 456, 'name': 'C'}])
    joined = join_price_minmax(df, pm, appid_col='appid')
    assert 'price_min' in joined.columns and 'price_max' in joined.columns
    assert joined.loc[joined['appid'] == 123, 'price_min'].iloc[0] == 1.99
    assert joined.loc[joined['appid'] == 789, 'price_samples_count'].iloc[0] == 1
    # missing appid -> samples_count 0
    assert joined.loc[joined['appid'] == 456, 'price_samples_count'].iloc[0] == 0
