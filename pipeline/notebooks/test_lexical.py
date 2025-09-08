#!/usr/bin/env python3
"""Test lexical search directly"""

import sqlite3

def test_lexical_search():
    conn = sqlite3.connect('../data/phase2_hybrid_search.db')
    cursor = conn.cursor()
    
    query = "farming simulation"
    
    # Test direct FTS5 search
    print("=== Direct FTS5 Search ===")
    cursor.execute("""
        SELECT rowid, review_text, rank 
        FROM reviews_fts 
        WHERE reviews_fts MATCH ?
        ORDER BY rank
        LIMIT 5
    """, (query,))
    
    direct_results = cursor.fetchall()
    print(f"Direct FTS5 results for '{query}': {len(direct_results)}")
    for result in direct_results:
        print(f"  ID {result[0]}: rank={result[2]:.4f}, text={result[1][:50]}...")
    
    # Test with JOIN as in hybrid search
    print(f"\n=== JOIN Search (as in hybrid search) ===")
    cursor.execute("""
        SELECT r.id, r.app_id, r.review_text, r.quality_score,
               a.name as app_name, fts.rank
        FROM reviews_fts fts
        JOIN reviews r ON r.id = fts.rowid
        JOIN apps a ON a.app_id = r.app_id
        WHERE reviews_fts MATCH ?
        ORDER BY fts.rank
        LIMIT 5
    """, (query,))
    
    join_results = cursor.fetchall()
    print(f"JOIN results for '{query}': {len(join_results)}")
    for result in join_results:
        print(f"  ID {result[0]}: app={result[4]}, rank={result[5]:.4f}, text={result[2][:50]}...")
    
    # Test simple query
    print(f"\n=== Simple Query ===")
    cursor.execute("""
        SELECT rowid, review_text
        FROM reviews_fts 
        WHERE reviews_fts MATCH 'game'
        LIMIT 3
    """)
    
    simple_results = cursor.fetchall()
    print(f"Simple 'game' results: {len(simple_results)}")
    for result in simple_results:
        print(f"  {result[0]}: {result[1][:50]}...")
    
    conn.close()

if __name__ == "__main__":
    test_lexical_search()
