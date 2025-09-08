#!/usr/bin/env python3
"""Test queries with our actual game data"""

import sqlite3

def test_realistic_queries():
    conn = sqlite3.connect('../data/phase2_hybrid_search.db')
    
    # Test with keywords that should match our games
    queries = ['tycoon', 'battle', 'fantasy', 'survival', 'war', 'puzzle', 'game', 'good', 'bad']
    
    for query in queries:
        cursor = conn.execute('''
            SELECT rowid, review_text, rank 
            FROM reviews_fts 
            WHERE reviews_fts MATCH ?
            ORDER BY rank
            LIMIT 3
        ''', (query,))
        
        results = cursor.fetchall()
        print(f'Query: "{query}" -> {len(results)} results')
        for result in results:
            print(f'  {result[0]}: rank={result[2]:.4f}, text={result[1][:50]}...')
        print()
    
    conn.close()

if __name__ == "__main__":
    test_realistic_queries()
