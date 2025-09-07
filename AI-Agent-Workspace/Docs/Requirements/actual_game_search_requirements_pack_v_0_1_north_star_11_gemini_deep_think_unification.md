# Actual Game Search — Requirements Pack v0.1

**North Star:** `11_Gemini_DeepThink_Unification.md`

> Purpose: Provide a complete, AI‑developer‑friendly set of requirements to ship an ultra‑low‑cost, ultra‑high‑quality hybrid full‑text + semantic search engine for games at **actualgamesearch.com**, optimized for GitHub Copilot Agent Mode + GPT‑5.

---

## 0) Quick Read (What we’re building)
A Cloudflare‑first, polyglot system: TypeScript Workers + Pages for live API/UI; Python for ETL. Lexical recall in **D1/FTS5**, semantic re‑ranking in **Vectorize** using **nomic‑embed‑text:v1.5 (768‑D)**. One review‑embedding per review (≤200 per game). User‑tunable ranking with lightweight sliders; no LLM interpretation for facets/tags—use Steam metadata as ground truth. Offline ETL runs via Cloudflare Containers orchestrated by Workers Cron.

---

## 1) Product Requirements (PRD)

### 1.1 Vision & Outcomes
- **Vision:** Make it easy to *actually* find games users want by combining precise keyword filters with semantic understanding of rich review text.
- **Primary Outcomes:**
  1) Fast, relevant search (top‑3 contains at least one “good” hit for ≥65% of benchmark intents),
  2) Ultra‑low cost at hobby scale, scalable to millions of reviews,
  3) Open‑source template others can fork to build similar hybrid search.

### 1.2 Users & Use Cases
- **Players** discovering niche games by vibe/description intent.
- **Curators/Press** exploring relatedness graphs.
- **Developers** forking the repo as a base template.

### 1.3 Key Scenarios
- Search: *“cozy farming sim with relationship stories, not combat”* → filters + lexical recall; semantic re‑rank.
- “More like this” from a game page → nearest‑neighbors using review embeddings.
- Live weight tuning: sliders for **Relevance / Reputation / Recency / Repetition (4R)** adjust ranking in real time.

### 1.4 Non‑Goals
- No LLM labeling or regex taxonomies for genre/mechanics (multilingual & bias concerns).
- No user accounts at launch.

### 1.5 Success Metrics
- **Quality:** nDCG@10 ≥ 0.40 on gold‑set; Top‑3 Hit ≥ 65%.
- **Latency (P95):** API ≤ 300 ms for filtered Top‑K=200 pipeline (edge, warm).
- **Cost:** Initial monthly infra <$25; per‑1k‑queries cost target < $0.10 (excluding one‑time ETL embedding).

---

## 2) System Requirements (SRS)

### 2.1 Functional Requirements (IDs are authoritative)

**FR‑001 Search API**
- Accepts query string, structured filters (tags/platform/year/price), and optional user weights for 4R.
- Executes **two‑stage hybrid pipeline**:
  1) **D1/FTS5 lexical recall** + filters → candidate product_ids (Top‑K = 500–1000),
  2) **Vectorize** ANN query of the same text embedding → semantic scores on candidates,
  3) **Fusion** via RRF → 4R scoring with user‑tunable weights.
- Returns paged results with highlights, facet counts, and debug signals (scores per component).

**FR‑002 Autocomplete**
- Prefix search on titles/tags using FTS5; returns up to 10 suggestions.

**FR‑003 “More Like This”**
- Given a product_id, compute semantic neighbors from review‑level vectors (filtered to that game’s embeddings or averaged per game). Expose both strategies behind a flag.

**FR‑004 Facets & Filters**
- Facets: platform, tags, controller support, languages, release year, price, review‑count buckets.
- Source from Steam metadata only; **no** LLM inference pipeline.

**FR‑005 Weights UI (4R Sliders)**
- Client sends weights: `relevance`, `reputation`, `recency`, `repetition` in [0..1]. Persist in URL query state.

**FR‑006 Observability**
- Health: `/healthz` (worker), `/readyz` (DB reachability). Metrics counters: request counts, latency histograms, vector queries/sec.

**FR‑007 Admin/ETL Controls**
- Trigger ETL container from a Worker (cron/manual). ETL jobs are idempotent; partial failure retries by batch.

**FR‑008 i18n**
- Retain multilingual text as‑is; do not filter by language unless requested.

**FR‑009 OSS Template Mode**
- Repo includes `TEMPLATE_GUIDE.md` for forkers + `./tasks` playbooks for Copilot Agent.

### 2.2 Data Requirements
- **Embeddings:** `nomic-embed-text:v1.5`, 768‑D; **1 per review**, ≤200 reviews per product (hard cap). Optional single embeddings for description/metadata.
- **D1 Schema (SQLite + FTS5):**
  - `products(id, appid, title, short_desc, long_desc, release_date, price_final, is_free, tags_json, platform_json, controller_support, reputation_score, review_count, updated_at)`
  - `reviews(id, appid, language, voted_up, processed_text, word_count, unique_word_count, resonance_score, time_weighted_resonance, created_at, updated_at)`
  - `products_fts` (FTS5) on `title, short_desc, long_desc, tags_lexical` with BM25 ranking.
- **Vectorize Index:**
  - `ags_vectors(dim=768, metric=cosine)`
  - Metadata: `{ product_id, kind: 'review'|'desc', rating?, helpfulness?, ts }`

### 2.3 Non‑Functional Requirements (NFRs)
- **Performance:** P95 end‑to‑end ≤ 300 ms for Top‑K=200 semantic step at warm edge; cold ≤ 900 ms.
- **Scalability:** Support tens of millions of review vectors via sharded indexes and filtered ANN on candidate lists.
- **Cost:** Prefer free/low tiers: Workers, Pages, D1, Vectorize, R2. ETL runs batched/scheduled to minimize usage.
- **Reliability:** Error budget 99.5% monthly availability for API; graceful degrade to lexical‑only if Vectorize unavailable.
- **Security:** No PII; CORS locked to site; read‑only public API with rate limits; admin routes gated by token.
- **Accessibility:** WCAG 2.1 AA for UI.

---

## 3) Architecture Overview (Cloudflare‑First)

**Front Door:** Cloudflare **Pages** (UI) + **Workers** (API).  
**Core Data:** **D1/FTS5** for metadata + lexical; **Vectorize** for semantic; **R2** for raw dumps.  
**Batch:** **Cloudflare Containers** (Python ETL), orchestrated by a **Worker Cron** via **Durable Object** for job state.  
**Pattern:** Worker‑as‑orchestrator; Container for long‑running ETL; sequential hybrid retrieval; RRF→4R scoring in Worker.

Sequence (Search):
1) UI → Worker `/search` with query, filters, weights.  
2) Worker → D1/FTS5 for candidates (Top‑K ids).  
3) Worker → Vectorize with metadata filter `product_id in {ids}`; get semantic scores.  
4) Worker → fuse + 4R weighting → return results.

Sequence (ETL):
1) Cron Worker → Durable Object → start Container job.  
2) Container pulls new metadata/reviews → preprocess → embed → bulk upsert: D1 + Vectorize.  
3) Emit run logs & metrics; update `updated_at` watermark.

---

## 4) API Requirements (first cut)

### 4.1 `POST /search`
**Request**
```json
{
  "q": "cozy farming sim with relationships",
  "filters": {
    "platform": ["windows"],
    "tags": ["farming", "life-sim"],
    "release_year_min": 2015,
    "price_max": 30
  },
  "weights": { "relevance": 0.55, "reputation": 0.2, "recency": 0.15, "repetition": 0.1 },
  "page": 1,
  "page_size": 20
}
```
**Response**
```json
{
  "results": [
    {
      "product_id": 12345,
      "title": "Stardew Valley",
      "score": 0.812,
      "signals": {"bm25": 0.73, "sim": 0.84, "rrf": 0.78, "4r": {"relevance": 0.78, "reputation": 0.9, "recency": 0.4, "repetition": 0.6}},
      "facets": {"tags": ["farming", "life-sim"], "platform": ["windows"]}
    }
  ],
  "facets": {"tags": {"farming": 124, "life-sim": 87}, "platform": {"windows": 645}},
  "debug": {"candidate_count": 800, "vector_k": 200}
}
```

### 4.2 `GET /suggest?q=star`
- Returns up to 10 suggestions (titles/tags).

### 4.3 `GET /similar/:product_id`
- Returns Top‑K neighbors using review vectors; includes a flag to switch to game‑embedding (averaged) mode.

### 4.4 Health
- `GET /healthz`, `GET /readyz` with dependency checks.

---

## 5) ETL Requirements

### 5.1 Sources
- Steam apps list, per‑app metadata JSON, and per‑app reviews (respect rate limits & ToS). Store raw in **R2**.

### 5.2 Filtering
- Keep only **released** games; exclude 18+; drop duplicates; require **≥20** qualifying reviews; drop gifted and short (unique words < 20). Preserve multilingual text.

### 5.3 Processing
- Preprocess text (HTML strip, whitespace normalize; keep language). Compute review stats (e.g., resonance, time‑weighted resonance). Cap **≤200 reviews per game** for embeddings.

### 5.4 Embedding
- Model: **nomic‑embed‑text:v1.5** (768‑D). One vector per review; optional per‑game description and/or metadata vector.

### 5.5 Load
- Bulk upsert **D1** (products, reviews, FTS virtual table). Bulk insert **Vectorize** with metadata.

### 5.6 Orchestration & Ops
- Schedule via **Cron Worker** → **Durable Object** → **Container**. Idempotent batches. On failure, retry with exponential backoff per batch. Emit run metrics and state to D1 `etl_runs`.

---

## 6) Ranking & Fusion

### 6.1 Candidate Generation
- FTS5 MATCH with filters → Top‑K ids (K configurable 500–1000). Return BM25 scores.

### 6.2 Semantic Re‑ranking
- ANN on Vectorize with query embedding; **metadata filter to candidate ids**. Return similarity scores (cosine).

### 6.3 Fusion & Final Score
- **RRF**: `rrf = 1/(k + rank_lex) + 1/(k + rank_sem)` (k≈60).  
- **4R** components:
  - **Relevance** = normalized fusion score (BM25 + sim via RRF),
  - **Reputation** = Bayesian prior from review counts/helpfulness/positivity (precomputed in D1),
  - **Recency** = exponential decay vs. release date,
  - **Repetition** = boost if multiple distinct reviews for the same game surface in Top‑K.
- **Final:** `score = w_rel*Rel + w_rep*Rep + w_rec*Rec + w_rep2*Repeat` (weights from client or defaults). Normalize for stable UX.

---

## 7) Quality, Testing & Evaluation

### 7.1 Gold‑Set
- 100–200 query→ideal‑set pairs spanning genres/tones/languages. Curate over time.

### 7.2 Automated Tests
- **Unit:** ETL transforms, SQL queries, fusion math.  
- **Integration:** End‑to‑end search happy‑paths; fallback to lexical‑only if Vectorize down.  
- **Load:** k6/Gatling smoke at 50 rps; ensure P95 targets.

### 7.3 Eval Jobs
- Offline notebook computes **nDCG@10**, **MRR**, **Recall@K** over gold‑set per release.

---

## 8) AI‑Driven Development Enablement

### 8.1 Repo Scaffolding
- **Polyglot monorepo:** `platform/*` (TS) + `etl/*` (Python).  
- `./docs`, `./docs/adr`, `./tasks` (Copilot playbooks), `./.github` (workflows + issue templates), `./.vscode` (settings).

### 8.2 Copilot Agent Playbooks (examples in `/tasks`)
- `task_search_api_first_pass.md`: Implement `/search` pipeline skeleton.  
- `task_vectorize_client.md`: Create Vectorize client wrapper with filtered‑ANN helper.  
- `task_rrf_4r.md`: Implement RRF + 4R scoring with unit tests.  
- `task_d1_schema.md`: Create D1 schema + migrations + FTS5.

### 8.3 Grounding Docs
- `copilot-instructions.md` (project mission, constraints, behavioral expectations).  
- ADRs capture irreversible decisions; Agent references **#file** links in prompts.

### 8.4 Guardrails
- CI: typecheck, lint, unit tests.  
- Pre‑commit hooks (format, simple static checks).  
- “Do → Verify → Document” enforced via PR template checklists.

---

## 9) Release Plan
- **M0 (Week 0–1):** Repo scaffold; D1 schema; stub Worker/API; UI shell; CI.
- **M1 (Week 1–2):** ETL container MVP; ingest 10k games sample; embed; load D1+Vectorize.
- **M2 (Week 2–3):** Hybrid search path end‑to‑end; sliders; metrics.
- **M3 (Week 3–4):** Quality evals; k6 load; accessibility; public beta.

---

## 10) Risks & Mitigations
- **Cloudflare limits / beta services:** Keep lexical‑only fallback; small, explicit batch sizes; feature flags.  
- **Data licensing / ToS drift:** Track Steam API terms; document compliance; kill‑switch in Worker.  
- **Cost spikes (embeddings/vector ops):** Cap review count; batch schedules; monitor usage dashboards.

---

## 11) Glossary
- **FTS5:** SQLite full‑text search extension with BM25 ranking.
- **Vectorize:** Cloudflare’s vector DB for ANN similarity search.
- **RRF:** Reciprocal Rank Fusion to combine ranked lists.
- **4R:** Relevance, Reputation, Recency, Repetition.

---

## 12) Acceptance Criteria (Sample)
- **AC‑S01:** `/search` returns deterministic JSON with `signals` and `facets` for a canned query in seeded data.  
- **AC‑S02:** Fallback to lexical‑only when Vectorize is unreachable is covered by an automated test.  
- **AC‑ETL01:** ETL job idempotently re‑runs without duplicating vectors/rows (checked by primary keys + metadata).  
- **AC‑UI01:** Weight sliders modify result order without full reload and reflect in URL state.

---

## 13) Appendix
- Proposed table DDLs, Vectorize index template, and request/response JSON examples will evolve with ADRs during M0/M1.

