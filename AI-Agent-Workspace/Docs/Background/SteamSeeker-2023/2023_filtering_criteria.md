# SteamSeeker (2023) — Filtering & Inclusion Criteria (consolidated)

This document summarizes the stepwise filtering and review selection heuristics used in the 2023 SteamSeeker pipeline. Use this as the canonical reference when reproducing or adapting the 2023 filtering logic.

## High-level goals
- Produce a clean corpus of consumer-facing games (not DLCs, soundtracks, or unlisted items).
- Ensure each game has a sufficient number of substantive user reviews (to support embeddings and ranking experiments).
- Remove low-signal and promotional artifacts (very short, gifted or duplicate reviews).
- Materialize nested keys (price, release flags) for robust downstream use.

## Stepwise app-level filters (applied to metadata)
1. Deduplicate by `steam_appid` (keep unique app rows).
2. Keep only rows where `type == 'game'`.
3. Exclude adult-only titles: `required_age` coerced numeric and keep `required_age < 18`.
4. Exclude unreleased / coming-soon titles: `release_date.coming_soon == False`.
5. Require presence of human-facing text:
   - `short_description` not null/empty
   - `detailed_description` (or `about_the_game`) not null/empty
6. Optional: remove unlisted games (some entries where `is_free == False` but `price_overview.final` is missing) — these are price-listing anomalies.
7. Remove obviously objectionable or non-game entries via a short list of filter words (e.g., `hentai`) applied to `name`, `short_description`, and `detailed_description`.
8. Keep only games that appear in the review census (i.e., have at least one collected review).

Notes:
- Price handling: convert `price_overview.initial`/`price_overview.final` from cents to float (divide by 100). Materialize `price_overview.final` and `price_overview.currency` when present; treat the absence of both and `is_free==False` as an unlisted item.

## Review-level filters (applied to reviews after joining to filtered apps)
1. Drop duplicate review texts (dedupe by `processed_review`).
2. Remove reviews with low lexical richness: `unique_word_count >= 20`.
3. Remove reviews which were `received_for_free == True` (gifted/promo reviews often lower signal).
4. Optionally, ignore non-consumer languages or languages not in the supported list (project-dependent).
5. Filter out games with too few qualifying reviews: require a minimum number of reviews per game (the 2023 pipeline used `min_reviews = 20`).

Derived columns and scoring
- Compute `days_since_review_posted` and a log-time divisor (example: `log365_days_since_review = max(1, log(days_since_review_posted, 365))`) then compute a `time_weighted_resonance = resonance_score / log365_days_since_review` to favor recent, resonant reviews.
- Bulk stats per game: positivity_rating (fraction voted_up==True), geometric means for word_count, unique_word_count, resonance_score, author.playtime_forever, author.num_games_owned, author.num_reviews.

Persistence and checkpoints
- Save filtered metadata and filtered reviews as Feather files for reproducible downstream ETL and embedding generation.

Rationale and tradeoffs
- Thresholds (unique words >= 20, min_reviews = 20) were chosen to balance corpus size with signal quality; they may be relaxed for long-tail coverage or tightened for higher precision.
- Removing gifted reviews and duplicates reduces promotional noise and replicated content that would bias embeddings and search.
- The pipeline intentionally materializes nested fields and prefers structured detection (i.e., canonical column map) rather than hard-coded strings.

Recommended next steps
- Treat these criteria as tunable: add a small validation harness that measures coverage and signal for different thresholds (e.g., min_reviews=5,10,20) and reports downstream impact on embedding coverage and ranking experiments.
- Persist the `COLUMN_MAP` that maps logical fields to actual dataset columns, and version it alongside saved filtered artifacts.

--
Generated from the SteamSeeker-2023 notes in this repo.
