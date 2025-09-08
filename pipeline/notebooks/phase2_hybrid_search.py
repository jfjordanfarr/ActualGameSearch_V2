#!/usr/bin/env python3
"""
Phase 2: Hybrid Search Implementation
ActualGameSearch V2 - FTS5 + Vector Fusion

Building on Phase 1 semantic search to create complete hybrid search pipeline.
"""

import pandas as pd
import numpy as np
import sqlite3
import json
import time
import requests
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Configuration
DATA_DIR = Path("../data")
OLLAMA_URL = "http://127.0.0.1:11434"
EMBEDDING_MODEL = "nomic-embed-text:v1.5"

class HybridSearchEngine:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.setup_database()
    
    def setup_database(self):
        """Setup SQLite database with FTS5 + vector tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Apps table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS apps (
                app_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                short_description TEXT,
                detailed_description TEXT,
                tags_json TEXT,
                reputation_score REAL,
                review_count INTEGER
            )
        """)
        
        # Reviews table with quality metrics
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY,
                app_id INTEGER,
                review_text TEXT,
                quality_score REAL,
                word_count INTEGER,
                voted_up BOOLEAN,
                language TEXT,
                FOREIGN KEY (app_id) REFERENCES apps (app_id)
            )
        """)
        
        # FTS5 virtual table for fast text search
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS reviews_fts USING fts5(
                review_text,
                content='reviews',
                content_rowid='id'
            )
        """)
        
        # Vector embeddings (from Phase 1)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS review_embeddings (
                id INTEGER PRIMARY KEY,
                app_id INTEGER,
                review_text TEXT,
                embedding_json TEXT,
                quality_score REAL
            )
        """)
        
        conn.commit()
        conn.close()
    
    def lexical_search(self, query: str, limit: int = 100) -> List[Dict]:
        """Stage 1: FTS5 lexical recall"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # FTS5 search with BM25 ranking
        cursor.execute("""
            SELECT r.id, r.app_id, r.review_text, r.quality_score,
                   a.name as app_name, fts.rank
            FROM reviews_fts fts
            JOIN reviews r ON r.id = fts.rowid
            JOIN apps a ON a.app_id = r.app_id
            WHERE reviews_fts MATCH ?
            ORDER BY fts.rank
            LIMIT ?
        """, (query, limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'app_id': row[1], 
                'review_text': row[2],
                'quality_score': row[3],
                'app_name': row[4],
                'lexical_score': row[5]
            })
        
        conn.close()
        return results
    
    def semantic_search(self, query_embedding: List[float], candidate_ids: List[int], limit: int = 50) -> List[Dict]:
        """Stage 2: Semantic search on lexical candidates"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if not candidate_ids:
            return []
        
        # Get embeddings for candidates only
        placeholders = ','.join(['?'] * len(candidate_ids))
        cursor.execute(f"""
            SELECT id, app_id, review_text, embedding_json, quality_score
            FROM review_embeddings 
            WHERE id IN ({placeholders})
        """, candidate_ids)
        
        results = []
        for row in cursor.fetchall():
            stored_embedding = json.loads(row[3])
            similarity = self.cosine_similarity(query_embedding, stored_embedding)
            results.append({
                'id': row[0],
                'app_id': row[1],
                'review_text': row[2],
                'quality_score': row[4],
                'semantic_score': similarity
            })
        
        # Sort by semantic similarity
        results.sort(key=lambda x: x['semantic_score'], reverse=True)
        conn.close()
        
        return results[:limit]
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        if np.linalg.norm(vec1) == 0 or np.linalg.norm(vec2) == 0:
            return 0.0
        
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    
    def hybrid_search(self, query: str, query_embedding: List[float], top_k: int = 20) -> List[Dict]:
        """Stage 3: Hybrid fusion with RRF"""
        # Stage 1: Lexical recall
        lexical_results = self.lexical_search(query, limit=100)
        candidate_ids = [r['id'] for r in lexical_results]
        
        if not candidate_ids:
            return []
        
        # Stage 2: Semantic search on candidates
        semantic_results = self.semantic_search(query_embedding, candidate_ids, limit=50)
        
        # Stage 3: Fusion with RRF (Reciprocal Rank Fusion)
        return self.reciprocal_rank_fusion(lexical_results, semantic_results, top_k)
    
    def reciprocal_rank_fusion(self, lexical_results: List[Dict], semantic_results: List[Dict], top_k: int) -> List[Dict]:
        """Combine lexical and semantic results with RRF"""
        # Create lookup maps
        lexical_map = {r['id']: (i+1, r) for i, r in enumerate(lexical_results)}
        semantic_map = {r['id']: (i+1, r) for i, r in enumerate(semantic_results)}
        
        # Calculate RRF scores
        rrf_scores = {}
        k = 60  # RRF parameter
        
        # All unique IDs from both result sets
        all_ids = set(lexical_map.keys()) | set(semantic_map.keys())
        
        for doc_id in all_ids:
            score = 0.0
            
            # Add lexical contribution
            if doc_id in lexical_map:
                lexical_rank, lexical_doc = lexical_map[doc_id]
                score += 1.0 / (k + lexical_rank)
            
            # Add semantic contribution  
            if doc_id in semantic_map:
                semantic_rank, semantic_doc = semantic_map[doc_id]
                score += 1.0 / (k + semantic_rank)
            
            # Get document info (prefer semantic if available)
            doc_info = semantic_map.get(doc_id, lexical_map.get(doc_id))[1]
            
            rrf_scores[doc_id] = {
                'rrf_score': score,
                'doc_info': doc_info,
                'has_lexical': doc_id in lexical_map,
                'has_semantic': doc_id in semantic_map
            }
        
        # Sort by RRF score and return top-k
        sorted_results = sorted(rrf_scores.items(), key=lambda x: x[1]['rrf_score'], reverse=True)
        
        final_results = []
        for doc_id, data in sorted_results[:top_k]:
            result = data['doc_info'].copy()
            result['rrf_score'] = data['rrf_score']
            result['fusion_signals'] = {
                'has_lexical': data['has_lexical'],
                'has_semantic': data['has_semantic']
            }
            final_results.append(result)
        
        return final_results

def create_query_embedding(text: str) -> List[float]:
    """Create embedding for search query using Ollama"""
    try:
        payload = {"model": EMBEDDING_MODEL, "prompt": text}
        response = requests.post(
            f"{OLLAMA_URL}/api/embeddings",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("embedding", [])
        else:
            print(f"❌ Query embedding failed: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error creating query embedding: {e}")
        return []

def main():
    """Demo hybrid search implementation"""
    print("=== Phase 2: Hybrid Search Implementation ===")
    
    # Setup hybrid search engine
    db_path = str(DATA_DIR / "phase2_hybrid_search.db")
    search_engine = HybridSearchEngine(db_path)
    
    print(f"✅ Hybrid search database initialized: {db_path}")
    
    # Test queries that match our actual games
    test_queries = [
        "tycoon game",
        "battle strategy",
        "puzzle fun",
        "survival crafting",
        "good game"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing query: '{query}'")
        
        # Create query embedding
        query_embedding = create_query_embedding(query)
        
        if query_embedding:
            # Perform hybrid search
            results = search_engine.hybrid_search(query, query_embedding, top_k=5)
            
            print(f"Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(f"  {i}. RRF Score: {result['rrf_score']:.3f}")
                print(f"     App: {result.get('app_name', 'Unknown')}")
                print(f"     Text: {result['review_text'][:80]}...")
                print(f"     Signals: {result['fusion_signals']}")
        else:
            print("❌ Failed to create query embedding")
    
    print("\n🚀 Phase 2 hybrid search demo complete!")

if __name__ == "__main__":
    main()
