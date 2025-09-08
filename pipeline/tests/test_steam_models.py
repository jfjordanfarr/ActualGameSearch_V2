import json
import os
import sys
# Ensure pipeline/src is on sys.path so tests can import the package-style modules
repo_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
src_path = os.path.join(repo_dir, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from ags_pipeline.models.steam_models import PriceOverview, ReleaseDate, SimpleNamed, Requirements, AppDetail


def test_price_overview_from_cents():
    d = {'final': 1499, 'currency': 'USD'}
    p = PriceOverview.from_dict(d)
    assert p is not None
    assert isinstance(p.final, float)
    assert abs(p.final - 14.99) < 1e-6
    assert p.currency == 'USD'


def test_release_date_parsing():
    d = {'date': 'Sep 21, 2023', 'coming_soon': False}
    r = ReleaseDate.from_dict(d)
    assert r.date == 'Sep 21, 2023'
    assert r.coming_soon is False


def test_simple_named_and_requirements():
    sn = SimpleNamed.from_dict({'id': 1, 'name': 'Indie', 'description': 'Indie game'})
    assert sn.name == 'Indie'
    req = Requirements.from_dict({'minimum': '2 GB', 'recommended': '4 GB'})
    assert req.minimum == '2 GB'


def test_appdetail_from_dict_preserves_raw():
    sample = {
        'steam_appid': 12345,
        'name': 'Test Game',
        'price_overview': {'final': 499, 'currency': 'USD'},
        'release_date': {'date': 'Jan 1, 2020', 'coming_soon': False},
        'categories': [{'id': 1, 'description': 'Single-player'}],
        'some_custom_field': 'keep_me'
    }
    app = AppDetail.from_dict(sample)
    assert app.appid == 12345
    assert app.name == 'Test Game'
    assert app.price_overview.final == 4.99
    assert 'some_custom_field' in app.raw
