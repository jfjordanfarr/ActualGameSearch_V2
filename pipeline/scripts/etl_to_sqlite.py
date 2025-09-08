"""
ETL script: Load flattened Steam app metadata from CSV/Feather into SQLite with normalized schema.
- Loads apps from CSV (default) or Feather (if specified).
- Creates tables: apps, app_genres, app_categories.
- Extracts and loads genres/categories with normalized column names.
- Prints row counts and a sample query for validation.
"""
import os
import sys
import pandas as pd
import sqlite3
import json

# --- Config ---
DEFAULT_INPUT_CSV = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "expanded_sampled_apps.csv"))
DEFAULT_INPUT_FEATHER = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "expanded_sampled_apps.feather"))
DEFAULT_SQLITE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "ags_sample.db"))

# --- Helper: Robust DataFrame Loader ---
def load_flattened_df(csv_path=DEFAULT_INPUT_CSV, feather_path=DEFAULT_INPUT_FEATHER):
    if os.path.exists(feather_path):
        try:
            df = pd.read_feather(feather_path)
            print(f"Loaded DataFrame from Feather: {feather_path}")
            return df
        except Exception as e:
            print(f"Failed to load Feather: {e}")
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path, low_memory=False)
            print(f"Loaded DataFrame from CSV: {csv_path}")
            return df
        except Exception as e:
            print(f"Failed to load CSV: {e}")
    raise FileNotFoundError(f"Neither Feather nor CSV found at {feather_path} or {csv_path}")

# --- Helper: Extract genres/categories with normalized columns ---
def extract_list_field(df, field, id_col="steam_appid"):
    rows = []
    id_col_out = "genre_id" if field == "genres" else "category_id"
    desc_col_out = "genre_desc" if field == "genres" else "category_desc"
    for _, row in df.iterrows():
        appid = row[id_col]
        try:
            items = json.loads(row.get(field, "[]")) if field in df.columns else []
        except Exception:
            items = []
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict) and "id" in item and "description" in item:
                    rows.append({id_col: appid, id_col_out: item["id"], desc_col_out: item["description"]})
    return pd.DataFrame(rows)

# --- Main ETL ---
def main():
    df = load_flattened_df()
    conn = sqlite3.connect(DEFAULT_SQLITE_PATH)

    # --- Create apps table ---
    apps_schema = '''
    CREATE TABLE IF NOT EXISTS apps (
        steam_appid INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        type TEXT,
        required_age INTEGER,
        is_free BOOLEAN,
        detailed_description TEXT,
        short_description TEXT,
        about_the_game TEXT,
        supported_languages TEXT,
        header_image TEXT,
        website TEXT,
        release_date TEXT,
        coming_soon BOOLEAN,
        platforms TEXT,
        metacritic_score INTEGER,
        recommendations INTEGER
        -- ... add more fields as needed
    );
    '''
    conn.execute(apps_schema)
    df.to_sql("apps", conn, if_exists="replace", index=False)
    print(f"Loaded {len(df)} apps into SQLite table 'apps'.")

    # --- Extract and load genres and categories ---
    genres_df = extract_list_field(df, "genres")
    categories_df = extract_list_field(df, "categories")

    genres_schema = '''
    CREATE TABLE IF NOT EXISTS app_genres (
        steam_appid INTEGER,
        genre_id INTEGER,
        genre_desc TEXT,
        PRIMARY KEY (steam_appid, genre_id)
    );
    '''
    categories_schema = '''
    CREATE TABLE IF NOT EXISTS app_categories (
        steam_appid INTEGER,
        category_id INTEGER,
        category_desc TEXT,
        PRIMARY KEY (steam_appid, category_id)
    );
    '''
    conn.execute(genres_schema)
    conn.execute(categories_schema)

    if not genres_df.empty:
        genres_df.to_sql("app_genres", conn, if_exists="replace", index=False)
    if not categories_df.empty:
        categories_df.to_sql("app_categories", conn, if_exists="replace", index=False)
    print(f"Loaded {len(genres_df)} genres and {len(categories_df)} categories into SQLite.")

    # --- Validation: Row counts and sample query ---
    apps_count = conn.execute("SELECT COUNT(*) FROM apps").fetchone()[0]
    genres_count = conn.execute("SELECT COUNT(*) FROM app_genres").fetchone()[0]
    categories_count = conn.execute("SELECT COUNT(*) FROM app_categories").fetchone()[0]
    print(f"apps: {apps_count}, genres: {genres_count}, categories: {categories_count}")

    sample_app = conn.execute("SELECT steam_appid, name FROM apps LIMIT 1").fetchone()
    if sample_app:
        appid, name = sample_app
        print(f"Sample app: {appid} - {name}")
        app_genres = conn.execute("SELECT genre_desc FROM app_genres WHERE steam_appid=?", (appid,)).fetchall()
        app_categories = conn.execute("SELECT category_desc FROM app_categories WHERE steam_appid=?", (appid,)).fetchall()
        print("Genres:", [g[0] for g in app_genres])
        print("Categories:", [c[0] for c in app_categories])
    conn.close()

if __name__ == "__main__":
    main()
