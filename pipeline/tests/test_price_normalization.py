import os, sys
repo_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
src_path = os.path.join(repo_dir, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from ags_pipeline.models.steam_models import PriceOverview


def test_usd_int_cents():
    p = PriceOverview.from_dict({'final': 499, 'currency': 'USD'})
    assert p.final == 4.99
    assert p.normalization_note == 'converted_by_currency'


def test_usd_float_presumed():
    p = PriceOverview.from_dict({'final': 4.99, 'currency': 'USD'})
    assert p.final == 4.99
    assert p.normalization_note == 'float_presumed_major'


def test_jpy_int_major():
    p = PriceOverview.from_dict({'final': 1500, 'currency': 'JPY'})
    assert p.final == 1500.0
    assert p.normalization_note == 'converted_by_currency_minor0'


def test_unknown_currency_assume_cents():
    p = PriceOverview.from_dict({'final': 1000})
    assert p.final == 10.0
    assert p.normalization_note == 'assumed_cents_no_currency'
