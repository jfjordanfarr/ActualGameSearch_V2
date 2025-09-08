# ETL Pipeline

See notebooks/ and src/ags_pipeline/ for details.
## Developer setup

Install runtime dependencies (pip):

```powershell
python -m pip install -r requirements.txt
```

Install development/test dependencies:

```powershell
python -m pip install -r requirements-dev.txt
```

Run tests (from `pipeline/`):

```powershell
# using the project's venv interpreter
.\.venv\Scripts\python.exe -m pytest -q
# or activate the venv and run pytest directly
'& '.\.venv\Scripts\Activate.ps1'
pytest -q
```

Run ETL (join price min/max into flattened apps and load into SQLite):

```powershell
$env:PYTHONPATH = 'pipeline/src'
D:/Projects/ActualGameSearch_V2/.venv/Scripts/python.exe pipeline/scripts/run_etl.py
```
