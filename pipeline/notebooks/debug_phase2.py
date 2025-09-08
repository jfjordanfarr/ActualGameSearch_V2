#!/usr/bin/env python3
"""Debug Phase 2 Database Contents"""

import sqlite3

def debug_database():
    conn = sqlite3.connect('../data/phase2_hybrid_search.db')
    
    print("=== Database Tables ===")
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        print(f"\nTable: {table_name}")
        
        # Count records
        count_cursor = conn.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = count_cursor.fetchone()[0]
        print(f"  Records: {count}")
        
        if count > 0:
            # Sample records
            sample_cursor = conn.execute(f"SELECT * FROM {table_name} LIMIT 2")
            samples = sample_cursor.fetchall()
            for i, sample in enumerate(samples):
                print(f"  Sample {i+1}: {sample[:3] if len(sample) > 3 else sample}")
    
    # Test FTS5 search
    print("\n=== FTS5 Test ===")
    fts_cursor = conn.execute("SELECT rowid, review_text FROM reviews_fts WHERE review_text MATCH 'game' LIMIT 3")
    fts_results = fts_cursor.fetchall()
    print(f"FTS5 'game' matches: {len(fts_results)}")
    for result in fts_results:
        print(f"  {result[0]}: {result[1][:50]}...")
    
    # Test embeddings
    print("\n=== Embeddings Test ===")
    emb_cursor = conn.execute("SELECT app_id, LENGTH(embedding_json) FROM review_embeddings LIMIT 3")
    emb_results = emb_cursor.fetchall()
    print(f"Embedding samples: {emb_results}")
    
    conn.close()

if __name__ == "__main__":
    debug_database()
