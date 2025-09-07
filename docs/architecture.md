
# Architecture

This document describes the architecture of Actual Game Search V2, both for local development and for the deployed Cloudflare environment. It includes diagrams and explanations of the main components, data flow, and how to run/verify the system locally.

---

## 1. High-Level Architecture Overview

```
┌──────────────────────────────┐
│         User Browser        │
└─────────────┬───────────────┘
		  │
		  ▼
	[Frontend Web App]
	   (SvelteKit/React)
		  │
		  ▼
	[Search API Worker]
	   (TypeScript)
	  ┌─────┴─────┐
	  │           │
	  ▼           ▼
[D1: SQLite+FTS5] [Vectorize]
   (Lexical)      (Semantic)
	  │           │
	  └─────┬─────┘
		  ▼
	   [Fusion/4R]
		  │
		  ▼
	   [Results]
```

---

## 2. Local Development Architecture

```
┌──────────────────────────────┐
│         User Browser        │
└─────────────┬───────────────┘
		  │
		  ▼
   Local Frontend (pnpm dev)
		  │
		  ▼
   Wrangler Dev (Search API)
		  │
	  ┌─────┴─────┐
	  │           │
	  ▼           ▼
 Local SQLite   Local Vector DB
 (D1 emulated)  (Vectorize emulated or mocked)
	  │           │
	  └─────┬─────┘
		  ▼
	   Fusion/4R
		  │
		  ▼
	   Results
```

**Local ETL Pipeline:**

```
┌──────────────┐
│  ETL Python  │
│  Pipeline    │
└──────┬───────┘
	 ▼
 [Raw Steam Data]
	 ▼
 [Preprocess/Embed]
	 ▼
 [Load to Local D1/Vector DB]
```

**How to Run/Verify Locally:**
- Run ETL pipeline: `cd pipeline && uv venv && uv pip install -e . && python src/ags_pipeline/main.py`
- Start API: `pnpm --filter platform/workers/search-api dev` (Wrangler dev)
- Start frontend: `pnpm --filter platform/apps/web dev`
- Point browser to local frontend, search, and verify results.

---

## 3. Deployed (Cloudflare) Architecture

```
┌──────────────────────────────┐
│         User Browser        │
└─────────────┬───────────────┘
		  │
		  ▼
   Cloudflare Pages (Web UI)
		  │
		  ▼
   Cloudflare Worker (API)
	  ┌─────┴─────┐
	  │           │
	  ▼           ▼
   D1 (Cloudflare)  Vectorize (Cloudflare)
	  │           │
	  └─────┬─────┘
		  ▼
	   Fusion/4R
		  │
		  ▼
	   Results
```

**ETL Pipeline (Deployed):**

```
┌──────────────┐
│  ETL Python  │
│  Container   │
└──────┬───────┘
	 ▼
 [Raw Steam Data in R2]
	 ▼
 [Preprocess/Embed]
	 ▼
 [Bulk Load to D1/Vectorize]
```

**How to Deploy/Verify (Proposed):**
- Deploy ETL as Cloudflare Container (manual or scheduled via Worker Cron)
- Deploy API Worker and Pages via Wrangler
- Use production web UI to search and verify results
- Monitor logs, metrics, and health endpoints (`/healthz`, `/readyz`)

---

## 4. Data Flow Summary

1. User enters search in web UI
2. API Worker parses query, runs D1 FTS5 + filters for candidates
3. API Worker queries Vectorize for semantic ranking (filtered to candidates)
4. API Worker fuses results (RRF + 4R)
5. Results returned to UI

---

For more details, see the requirements and research docs in `AI-Agent-Workspace/Docs/`.
