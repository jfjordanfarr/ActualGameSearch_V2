# Data Schema

## Rationale
Schema is based on real sampled Steam API data. Fields are included if present in all or most records, or if critical for search/ranking. Nested fields (genres, categories) are normalized for efficient querying and filtering.

## Tables

### apps
| Column              | Type    | Description                                 |
|---------------------|---------|---------------------------------------------|
| steam_appid         | int     | Steam app ID (PK)                           |
| name                | str     | Game name                                   |
| type                | str     | 'game', 'dlc', etc.                         |
| required_age        | int     | Age restriction                             |
| is_free             | bool    | Free to play                                |
| detailed_description| str     | Full description                            |
| short_description   | str     | Short description                           |
| about_the_game      | str     | About section                               |
| supported_languages | str     | Languages (raw string)                      |
| header_image        | str     | Header image URL                            |
| website             | str     | Website URL                                 |
| release_date        | str     | Release date (raw string)                   |
| coming_soon         | bool    | If unreleased                               |
| platforms           | str     | JSON or CSV of supported platforms          |
| metacritic_score    | int     | Metacritic score (if present)               |
| recommendations     | int     | Number of recommendations                   |
| ...                 | ...     | (other fields as needed)                    |

### app_genres
| steam_appid | genre_id | genre_desc |
|-------------|----------|------------|

### app_categories
| steam_appid | category_id | category_desc |
|-------------|-------------|--------------|

### reviews
| recommendationid | steam_appid | author_steamid | review | votes_up | votes_funny | voted_up | timestamp_created | language |
|------------------|------------|---------------|--------|----------|-------------|----------|-------------------|----------|

## Example: Field Presence (from sampled data)

**apps:**
- Always present: steam_appid, name, type, required_age, is_free, detailed_description, short_description
- Optional: metacritic, website, recommendations, header_image
- Nested: genres (list), categories (list), platforms (dict)

**reviews:**
- Always present: recommendationid, author_steamid, review, votes_up, votes_funny, voted_up, timestamp_created, language

## See also
- infra/d1_schema.sql for the actual SQL table definitions
- pipeline/notebooks/03_acquire_explore_etl_search.ipynb for profiling and ETL code
