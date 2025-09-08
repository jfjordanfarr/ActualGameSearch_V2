import os
import sys

# Ensure pipeline/src is on path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from ags_pipeline.transform import field_locator as fl


class DummySeries:
    def __init__(self, values):
        self._values = values

    def dropna(self):
        return DummySeries([v for v in self._values if v is not None])

    def head(self, n):
        return self._values[:n]


class DummyDF:
    def __init__(self, data: dict):
        self._data = data
        self.columns = list(data.keys())

    def __getitem__(self, col):
        return DummySeries(self._data[col])


def test_detect_and_get_value_without_pandas():
    # Create dummy data similar to what pandas would provide
    df_meta = DummyDF({
        'steam_appid': [1, 2],
        'price_overview': [
            {'final': 999, 'currency': 'USD'},
            '{"final": 499, "currency": "EUR"}'
        ]
    })

    df_rev = DummyDF({'app_id': [1], 'review_text': ['ok']})

    colmap = fl.build_column_map(df_meta, df_rev)

    assert colmap['app_id'] in ('steam_appid', 'appid', 'app_id')
    assert colmap['price_final'] is not None

    # Build simple row dicts for testing get_value_from_row
    row0 = {k: v[0] for k, v in df_meta._data.items()}
    row1 = {k: v[1] for k, v in df_meta._data.items()}

    assert fl.get_value_from_row(row0, colmap['price_final']) == 999
    assert fl.get_value_from_row(row1, colmap['price_final']) == 499

    cur0 = fl.get_value_from_row(row0, colmap['price_currency'])
    cur1 = fl.get_value_from_row(row1, colmap['price_currency'])
    assert cur0 == 'USD' or cur1 == 'EUR'
