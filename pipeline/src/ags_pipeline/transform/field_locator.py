import json
from typing import Any, Dict, List, Optional, Tuple, Union, Set


def detect_nested_keys(df, col: str, sample_n: int = 50) -> Set[str]:
    """Return a set of keys found inside dict or JSON-string values in df[col]."""
    keys: Set[str] = set()
    if df is None or col not in df.columns:
        return keys
    for v in df[col].dropna().head(sample_n):
        if isinstance(v, dict):
            keys.update(v.keys())
        elif isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, dict):
                    keys.update(parsed.keys())
            except Exception:
                continue
    return keys


candidates: Dict[str, List[str]] = {
    'app_id': ['steam_appid', 'appid', 'app_id'],
    'name': ['name', 'title'],
    'type': ['type'],
    'required_age': ['required_age', 'age'],
    'is_free': ['is_free', 'free'],
    'release_coming_soon': ['release_date.coming_soon', 'release_date', 'coming_soon'],
    'short_description': ['short_description', 'short_desc'],
    'detailed_description': ['detailed_description', 'description', 'about_the_game'],
    'price_final': ['price_overview.final', 'price_overview', 'final_price', 'price'],
    'price_currency': ['price_overview.currency', 'currency', 'price_currency'],
    'genres': ['genres'],
    'categories': ['categories'],
    'processed_review': ['processed_review', 'review_text', 'text', 'review'],
    'unique_word_count': ['unique_word_count', 'unique_words'],
    'received_for_free': ['received_for_free', 'received_for_free_bool']
}


def find_candidate(df_meta, df_rev, alt_list: List[str]) -> Optional[Union[str, Tuple[str, str]]]:
    """Return either a direct column name (str) or a tuple (parent_col, key) for nested keys.

    The function checks several heuristics:
    - dotted candidates like 'price_overview.final' (parent 'price_overview' contains key 'final')
    - direct column names in df_meta or df_rev
    - parent columns in df_meta that contain dict/json values with the candidate key
    """
    # check dotted names first
    for alt in alt_list:
        if '.' in alt:
            parent, subk = alt.split('.', 1)
            if df_meta is not None and parent in df_meta.columns:
                keys = detect_nested_keys(df_meta, parent)
                if subk in keys:
                    return (parent, subk)
        # direct column name
        for df in (df_meta, df_rev):
            if df is None:
                continue
            if alt in df.columns:
                return alt

    # try parent columns that contain dicts and have the subkey
    if df_meta is not None:
        for col in df_meta.columns:
            keys = detect_nested_keys(df_meta, col)
            for alt in alt_list:
                if isinstance(alt, str) and alt in keys:
                    return (col, alt)

    return None


def build_column_map(df_meta, df_rev) -> Dict[str, Optional[Union[str, Tuple[str, str]]]]:
    colmap: Dict[str, Optional[Union[str, Tuple[str, str]]]] = {}
    for logical, alts in candidates.items():
        colmap[logical] = find_candidate(df_meta, df_rev, alts)
    return colmap


def get_value_from_row(row: Union[Dict[str, Any], Any], locator: Optional[Union[Tuple[str, str], str]]) -> Any:
    """Read a value from a row by locator which can be a column name or (parent, key).

    Works with both dict-like rows and objects with attributes (e.g., pandas Series).
    """
    if locator is None:
        return None

    # locator is a tuple -> (parent_col, key)
    if isinstance(locator, tuple):
        parent, key = locator
        # support dict-like rows and attribute access
        if isinstance(row, dict):
            val = row.get(parent, None)
        else:
            val = getattr(row, parent, None)

        if isinstance(val, dict):
            return val.get(key)
        if isinstance(val, str):
            try:
                parsed = json.loads(val)
                if isinstance(parsed, dict):
                    return parsed.get(key)
            except Exception:
                return None
        return None

    # locator is a simple column name
    if isinstance(row, dict):
        return row.get(locator)
    return getattr(row, locator, None)


__all__ = ['detect_nested_keys', 'find_candidate', 'build_column_map', 'get_value_from_row', 'candidates']
