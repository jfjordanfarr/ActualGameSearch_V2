from pathlib import Path
import pandas as pd

from ags_pipeline.io.price_minmax_loader import load_price_minmax
from pipeline.scripts import run_etl as run


def test_join_and_replace_produces_price_columns(tmp_path: Path):
    # Ensure price_minmax.json exists
    pm = load_price_minmax()
    assert isinstance(pm, dict) and len(pm) >= 0

    # Run join step (in-place with backups) on repo data
    run.join_and_replace()

    data_dir = Path(__file__).resolve().parents[2] / 'pipeline' / 'data'
    csvp = data_dir / 'expanded_sampled_apps.csv'
    assert csvp.exists(), 'expected expanded_sampled_apps.csv after join'
    df = pd.read_csv(csvp, low_memory=False)
    for col in ['price_min', 'price_max', 'price_samples_count']:
        assert col in df.columns, f'missing {col} in expanded_sampled_apps.csv'
