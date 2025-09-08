#!/usr/bin/env python3
"""
Phase 1: Embeddings Integration with Ollama
ActualGameSearch V2 - Complete implementation
"""

import pandas as pd
import numpy as np
import requests
import json
import sqlite3
import time
import os
from pathlib import Path
from typing import List, Tuple, Optional

# Configuration
OLLAMA_URL = "http://127.0.0.1:11434"
EMBEDDING_MODEL = "nomic-embed-text:v1.5"
MAX_REVIEWS_PER_GAME = 200
DATA_DIR = Path("../data")

class OllamaEmbedder:
    def __init__(self, base_url: str = OLLAMA_URL, model: str = EMBEDDING_MODEL):
        self.base_url = base_url
        self.model = model
        self.embedding_url = f"{base_url}/api/embeddings"
        
    def test_connection(self) -> bool:
        """Test if ollama server is responsive"""
        try:
            response = requests.get(f"{self.base_url}/api/version", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def create_embedding(self, text: str) -> Optional[List[float]]:
        """Create embedding for a single text"""
        try:
            payload = {
                "model": self.model,
                "prompt": text
            }
            response = requests.post(
                self.embedding_url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload),
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("embedding", [])
            else:
                print(f"❌ Embedding failed: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error creating embedding: {e}")
            return None

def calculate_review_quality_score(review_row) -> float:
    """Calculate quality score for review selection"""
    score = 0.0
    
    # Helpfulness votes
    helpful_votes = review_row.get('votes_helpful', 0) or 0
    if pd.notna(helpful_votes) and helpful_votes > 0:
        score += float(helpful_votes) * 0.4
    
    # Review length and detail
    review_text = str(review_row.get('review', '') or review_row.get('review_text', '') or '')
    word_count = len(review_text.split())
    
    # Sweet spot: 20-200 words
    if 20 <= word_count <= 200:
        score += 10
    elif 10 <= word_count < 20:
        score += 5
    elif word_count > 200:
        score += 8
    
    # Base score
    if word_count > 0:
        score += 1
    
    # Penalties
    if word_count < 5:
        score -= 5
    
    return max(score, 0)

def select_top_reviews_per_game(reviews_df: pd.DataFrame, max_reviews: int = MAX_REVIEWS_PER_GAME) -> pd.DataFrame:
    """Select top quality reviews per game"""
    if reviews_df.empty or 'app_id' not in reviews_df.columns:
        return reviews_df
    
    reviews_df = reviews_df.copy()
    reviews_df['quality_score'] = reviews_df.apply(calculate_review_quality_score, axis=1)
    
    selected_reviews = []
    
    for app_id in reviews_df['app_id'].unique():
        game_reviews = reviews_df[reviews_df['app_id'] == app_id].copy()
        game_reviews = game_reviews.sort_values('quality_score', ascending=False)
        top_reviews = game_reviews.head(max_reviews)
        selected_reviews.append(top_reviews)
    
    return pd.concat(selected_reviews, ignore_index=True) if selected_reviews else pd.DataFrame()

def prepare_review_text(review_row) -> str:
    """Prepare combined text for embedding"""
    review_text = str(review_row.get('review', '') or 
                     review_row.get('review_text', '') or 
                     review_row.get('text', '') or '')
    
    title = str(review_row.get('title', '') or review_row.get('review_title', '') or '')
    
    if title and title.lower() != 'nan':
        combined_text = f"{title}\\n\\n{review_text}".strip()
    else:
        combined_text = review_text.strip()
    
    if not combined_text or combined_text.lower() == 'nan':
        combined_text = "No review text available"
    
    return combined_text

class VectorDatabase:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.setup_database()
    
    def setup_database(self):
        """Setup SQLite database with vector storage tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS review_embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                appid INTEGER NOT NULL,
                review_text TEXT NOT NULL,
                embedding_json TEXT NOT NULL,
                quality_score REAL,
                word_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_appid ON review_embeddings(appid)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_quality ON review_embeddings(quality_score DESC)")
        
        conn.commit()
        conn.close()
    
    def store_embeddings(self, reviews_df: pd.DataFrame) -> int:
        """Store embeddings in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM review_embeddings")
        
        stored_count = 0
        for _, row in reviews_df.iterrows():
            if row.get('embedding') is not None:
                cursor.execute("""
                    INSERT INTO review_embeddings 
                    (appid, review_text, embedding_json, quality_score, word_count)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    int(row['app_id']),
                    row['embedding_text'],
                    json.dumps(row['embedding']),
                    float(row.get('quality_score', 0)),
                    len(row['embedding_text'].split())
                ))
                stored_count += 1
        
        conn.commit()
        conn.close()
        return stored_count
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between vectors"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        if np.linalg.norm(vec1) == 0 or np.linalg.norm(vec2) == 0:
            return 0.0
        
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    
    def vector_search(self, query_embedding: List[float], top_k: int = 5) -> List[dict]:
        """Search for similar vectors"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, appid, review_text, embedding_json, quality_score, word_count 
            FROM review_embeddings
        """)
        
        results = []
        for row in cursor.fetchall():
            stored_embedding = json.loads(row[3])
            similarity = self.cosine_similarity(query_embedding, stored_embedding)
            results.append({
                'similarity': similarity,
                'id': row[0],
                'appid': row[1],
                'text': row[2],
                'quality_score': row[4],
                'word_count': row[5]
            })
        
        results.sort(key=lambda x: x['similarity'], reverse=True)
        conn.close()
        
        return results[:top_k]

def main():
    """Main Phase 1 implementation"""
    print("=== Phase 1: Embeddings Integration with Ollama ===")
    print(f"Data directory: {DATA_DIR.absolute()}")
    print(f"Ollama URL: {OLLAMA_URL}")
    print(f"Embedding model: {EMBEDDING_MODEL}")
    
    # Initialize embedder
    embedder = OllamaEmbedder()
    
    if not embedder.test_connection():
        print("❌ Cannot connect to ollama server")
        print("Please ensure ollama is running: ollama serve")
        return
    
    print("✅ Ollama server is running and responsive")
    
    # Test embedding
    test_embedding = embedder.create_embedding("Test game review")
    if not test_embedding or len(test_embedding) != 768:
        print("❌ Embedding test failed")
        return
    
    print("✅ Embeddings working correctly (768 dimensions)")
    
    # Load real Steam data
    print("\\n=== Loading Real Steam Data ===")
    try:
        apps_df = pd.read_feather(DATA_DIR / "resampled_apps.feather")
        reviews_df = pd.read_feather(DATA_DIR / "resampled_reviews.feather")
        print(f"✅ Loaded {len(apps_df)} apps and {len(reviews_df)} reviews")
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return
    
    if reviews_df.empty:
        print("❌ No review data available")
        return
    
    # Review selection
    print("\\n=== Review Quality Scoring and Selection ===")
    selected_reviews_df = select_top_reviews_per_game(reviews_df)
    
    print(f"Review selection results:")
    print(f"  Original reviews: {len(reviews_df)}")
    print(f"  Selected reviews: {len(selected_reviews_df)}")
    print(f"  Reduction: {((len(reviews_df) - len(selected_reviews_df)) / len(reviews_df) * 100):.1f}%")
    
    # Take sample for demonstration
    SAMPLE_SIZE = 20
    sample_reviews = selected_reviews_df.head(SAMPLE_SIZE).copy()
    print(f"\\n=== Creating Embeddings for {SAMPLE_SIZE} Sample Reviews ===")
    
    # Prepare review texts
    sample_reviews['embedding_text'] = sample_reviews.apply(prepare_review_text, axis=1)
    review_texts = sample_reviews['embedding_text'].tolist()
    
    print(f"Average text length: {np.mean([len(text.split()) for text in review_texts]):.1f} words")
    
    # Create embeddings
    print("Creating embeddings...")
    start_time = time.time()
    
    embeddings = []
    for i, text in enumerate(review_texts):
        embedding = embedder.create_embedding(text)
        embeddings.append(embedding)
        if (i + 1) % 5 == 0:
            print(f"  Processed {i + 1}/{len(review_texts)} embeddings")
        time.sleep(0.1)  # Be respectful to local server
    
    end_time = time.time()
    
    # Process results
    successful_embeddings = [e for e in embeddings if e is not None]
    
    print(f"\\n=== Embedding Results ===")
    print(f"  Total embeddings: {len(embeddings)}")
    print(f"  Successful: {len(successful_embeddings)}")
    print(f"  Success rate: {len(successful_embeddings)/len(embeddings)*100:.1f}%")
    print(f"  Total time: {end_time - start_time:.1f} seconds")
    print(f"  Average time per embedding: {(end_time - start_time)/len(embeddings):.2f} seconds")
    
    if not successful_embeddings:
        print("❌ No successful embeddings created")
        return
    
    # Add embeddings to dataframe
    sample_reviews['embedding'] = embeddings
    sample_reviews_with_embeddings = sample_reviews[sample_reviews['embedding'].notna()].copy()
    
    # Setup vector database
    print("\\n=== Setting up Vector Database ===")
    vector_db_path = str(DATA_DIR / "phase1_vector_prototype.db")
    vector_db = VectorDatabase(vector_db_path)
    
    stored_count = vector_db.store_embeddings(sample_reviews_with_embeddings)
    print(f"✅ Stored {stored_count} embeddings in vector database")
    
    # Test vector search
    print("\\n=== Testing Vector Search ===")
    
    test_queries = [
        "amazing graphics and beautiful visuals",
        "terrible bugs and poor controls", 
        "fun multiplayer with friends",
        "relaxing casual puzzle game"
    ]
    
    for query in test_queries:
        print(f"\\n🔍 Query: '{query}'")
        query_embedding = embedder.create_embedding(query)
        
        if query_embedding:
            results = vector_db.vector_search(query_embedding, top_k=3)
            
            for i, result in enumerate(results, 1):
                print(f"  {i}. Similarity: {result['similarity']:.3f} | AppID: {result['appid']} | Quality: {result['quality_score']:.1f}")
                print(f"     Text: {result['text'][:100]}{'...' if len(result['text']) > 100 else ''}")
    
    print("\\n=== Phase 1 Complete ===")
    print("✅ Ollama integration working")
    print("✅ Review selection implemented")
    print("✅ Vector storage functional")
    print("✅ Similarity search working")
    print("\\n🚀 Ready for Phase 2: Hybrid search implementation!")

if __name__ == "__main__":
    main()
