import sys
import os
import json

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
src_path = os.path.join(repo_root, 'pipeline', 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    from ags_pipeline.models import steam_models as sm
except Exception as e:
    print('Import failed:', e)
    raise

import pandas as pd

csv_p = os.path.join(repo_root, 'pipeline', 'data', 'resampled_apps.csv')
if not os.path.exists(csv_p):
    print('CSV not found:', csv_p)
    sys.exit(1)

df = pd.read_csv(csv_p)
if df.empty:
    print('CSV empty')
    sys.exit(1)

row = df.iloc[0].to_dict()
for c in ['price_overview','release_date','categories','genres','developers','publishers','pc_requirements','mac_requirements','linux_requirements']:
    if c in row and isinstance(row[c], str):
        try:
            row[c] = json.loads(row[c])
        except Exception:
            pass

app = sm.AppDetail.from_dict(row)
print('appid:', app.appid)
print('name:', app.name)
print('price:', app.price_overview)
print('release_date:', app.release_date)
print('categories count:', len(app.categories) if app.categories else 0)
print('developers:', app.developers)
