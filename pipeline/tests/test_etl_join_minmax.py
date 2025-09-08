from pathlib import Path
import pandas as pd
import shutil
import json

from ags_pipeline.io.price_minmax_loader import load_price_minmax, join_price_minmax


def test_join_and_replace_produces_price_columns(tmp_path: Path):
    """Test that joining price_minmax data adds the expected columns."""
    # Setup test fixtures
    fixtures_dir = Path(__file__).parent / 'fixtures'
    test_csv = tmp_path / 'expanded_sampled_apps.csv'
    test_json = tmp_path / 'price_minmax.json'
    
    # Copy test fixtures to temp directory
    shutil.copy(fixtures_dir / 'sample_expanded_apps.csv', test_csv)
    shutil.copy(fixtures_dir / 'sample_price_minmax.json', test_json)
    
    # Load test data
    df = pd.read_csv(test_csv, low_memory=False)
    with open(test_json, 'r') as f:
        pm_raw = json.load(f)
    
    # Convert string keys to int keys (as expected by join_price_minmax)
    pm = {int(k): v for k, v in pm_raw.items()}
    
    # Verify initial state - no price columns
    initial_columns = set(df.columns)
    price_columns = {'price_min', 'price_max', 'price_samples_count'}
    assert not price_columns.intersection(initial_columns), "Price columns should not exist initially"
    
    # Join price data
    appid_col = 'steam_appid' if 'steam_appid' in df.columns else 'appid'
    result_df = join_price_minmax(df, pm, appid_col=appid_col)
    
    # Verify price columns were added
    result_columns = set(result_df.columns)
    for col in price_columns:
        assert col in result_columns, f'missing {col} in result dataframe'
    
    # Verify data integrity
    assert len(result_df) == len(df), "Row count should be preserved"
    
    # Verify price data was joined correctly
    test_row = result_df[result_df['steam_appid'] == 12345].iloc[0]
    assert test_row['price_min'] == 9.99, "Price min should match fixture data"
    assert test_row['price_max'] == 19.99, "Price max should match fixture data"
    assert test_row['price_samples_count'] == 25, "Price samples count should match fixture data"