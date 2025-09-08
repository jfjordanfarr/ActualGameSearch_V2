# Phase 2: Hybrid Search Implementation - SQLite FTS5 + Vector Fusion

**Objective**: Implement the fulltext search component to complement our working Phase 1 semantic search, creating a complete hybrid search pipeline.

## Organization Standards for AI-Driven Development

**Notebook Naming Convention**:
- `01_data_exploration.ipynb` - Initial data analysis
- `02_ranking_evaluation.ipynb` - Quality metrics  
- `03_acquire_explore_etl_search.ipynb` - Data pipeline exploration
- `04_phase1_embeddings_ollama.ipynb` - Phase 1: Semantic search (✅ Complete)
- `05_phase2_hybrid_search.ipynb` - Phase 2: Fulltext + hybrid fusion (🔄 Current)

**Implementation Files**:
- `phase1_complete_implementation.py` - Working semantic search (✅ Complete)
- `phase2_hybrid_search.py` - This implementation (🔄 Current)
- `test_*.py` - Validation scripts

**Data Organization**:
- `data/` - Real Steam data (apps, reviews, embeddings)
- `data/phase1_vector_prototype.db` - Phase 1 vector storage (✅ Working)
- `data/phase2_hybrid_search.db` - Phase 2 FTS5 + hybrid storage (🔄 Target)

## Architecture Foundation (Based on 2023 SteamSeeker + Current Requirements)

### Filtering Pipeline (2023 Proven + 2025 Enhanced)
**App-Level Filters**:
- Keep only `type == 'game'` 
- Exclude adult content (`required_age < 18`)
- Exclude unreleased (`release_date.coming_soon == False`)
- Require description text (short + detailed not empty)
- Remove promotional/low-signal games

**Review-Level Filters**:
- Deduplicate by review text
- Minimum lexical richness (`unique_word_count >= 20`) - from 2023 criteria
- Remove gifted reviews (`received_for_free == False`)
- Quality-based selection (≤200 reviews per game) - our Phase 1 enhancement

### Hybrid Search Pipeline (New for 2025)
**Stage 1: FTS5 Lexical Recall**
- SQLite FTS5 index on review text + game metadata
- BM25 ranking for keyword relevance
- Fast candidate retrieval (Top-K = 500-1000)

**Stage 2: Semantic Re-ranking** 
- Use Phase 1 vector similarity on FTS5 candidates
- Nomic embeddings (768-D) with cosine similarity
- Filter to candidate product IDs from Stage 1

**Stage 3: Hybrid Fusion**
- Reciprocal Rank Fusion (RRF) combining lexical + semantic scores
- 4R weighting: Relevance, Reputation, Recency, Repetition
- User-tunable ranking parameters

### Data Schema (Production-Ready)
```sql
-- Apps table with FTS5 index
CREATE TABLE apps (
    app_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    short_description TEXT,
    detailed_description TEXT,
    release_date TEXT,
    price_final REAL,
    tags_json TEXT,
    platforms_json TEXT,
    reputation_score REAL,
    review_count INTEGER
);

-- Reviews table with quality metrics
CREATE TABLE reviews (
    id INTEGER PRIMARY KEY,
    app_id INTEGER,
    review_text TEXT,
    quality_score REAL,
    word_count INTEGER,
    unique_word_count INTEGER,
    voted_up BOOLEAN,
    language TEXT,
    created_at INTEGER,
    FOREIGN KEY (app_id) REFERENCES apps (app_id)
);

-- FTS5 virtual table for fast text search
CREATE VIRTUAL TABLE reviews_fts USING fts5(
    review_text, 
    app_name,
    content='reviews',
    content_rowid='id'
);

-- Vector embeddings (from Phase 1)
CREATE TABLE review_embeddings (
    id INTEGER PRIMARY KEY,
    app_id INTEGER,
    review_text TEXT,
    embedding_json TEXT,
    quality_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Implementation Plan

### ✅ Prerequisites Validated
- Phase 1 semantic search working (768-D embeddings, vector similarity)
- Real Steam data (20 apps, 1,204 reviews)  
- Ollama integration functional
- Quality scoring implemented

### 🔄 Phase 2 Tasks
1. **FTS5 Implementation**: SQLite full-text search setup
2. **Lexical Recall**: BM25 keyword search with filtering
3. **Candidate Pipeline**: FTS5 → product IDs → vector filtering
4. **Fusion Algorithm**: RRF implementation for score combination
5. **4R Scoring**: Relevance, Reputation, Recency, Repetition metrics
6. **Performance Testing**: Latency and relevance validation
7. **API-Ready Output**: JSON structure matching requirements spec

### 📊 Success Metrics
- **Latency**: Combined FTS5 + vector search < 300ms P95
- **Relevance**: Hybrid search outperforms pure semantic or lexical
- **Coverage**: Support filtering by platform, tags, price, release date
- **Quality**: Top-3 contains relevant results for test queries

---

This document serves as the architectural foundation for Phase 2 implementation. All code and notebooks should reference these standards and build incrementally on our proven Phase 1 foundation.
