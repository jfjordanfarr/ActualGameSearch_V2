#!/usr/bin/env python3
"""
Fix FTS5 Configuration in phase2_hybrid_search.db
Diagnose and repair the FTS5 virtual table that's causing the API blocking issue
"""

import sqlite3
from pathlib import Path

def diagnose_fts5_issue():
    """Diagnose what's wrong with the FTS5 table"""
    db_path = Path("pipeline/data/phase2_hybrid_search.db")
    
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔍 FTS5 Diagnosis")
    print("=" * 40)
    
    # Check all tables
    cursor.execute("SELECT name, type, sql FROM sqlite_master WHERE type IN ('table', 'view')")
    tables = cursor.fetchall()
    
    print("📋 All tables/views:")
    for name, table_type, sql in tables:
        print(f"  {table_type}: {name}")
        if 'fts' in name.lower():
            print(f"    SQL: {sql}")
    
    # Try to query the FTS5 table directly
    print("\n🧪 Testing FTS5 table access:")
    try:
        cursor.execute("SELECT COUNT(*) FROM reviews_fts")
        count = cursor.fetchone()[0]
        print(f"  ✅ reviews_fts accessible: {count} rows")
    except Exception as e:
        print(f"  ❌ reviews_fts error: {e}")
    
    # Check the structure of reviews_fts
    print("\n🏗️  FTS5 table structure:")
    try:
        cursor.execute("PRAGMA table_info(reviews_fts)")
        columns = cursor.fetchall()
        print(f"  Columns: {[col[1] for col in columns]}")
    except Exception as e:
        print(f"  ❌ Structure error: {e}")
    
    # Test a simple FTS5 query
    print("\n🔍 Testing FTS5 search:")
    try:
        cursor.execute("SELECT rowid FROM reviews_fts WHERE reviews_fts MATCH 'fun' LIMIT 1")
        result = cursor.fetchone()
        print(f"  ✅ FTS5 search works: {result}")
    except Exception as e:
        print(f"  ❌ FTS5 search error: {e}")
    
    conn.close()
    return True

def fix_fts5_table():
    """Recreate the FTS5 table properly"""
    db_path = Path("pipeline/data/phase2_hybrid_search.db")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n🔧 Fixing FTS5 Table")
    print("=" * 40)
    
    # Drop existing FTS5 table
    try:
        cursor.execute("DROP TABLE IF EXISTS reviews_fts")
        print("  🗑️  Dropped existing reviews_fts")
    except Exception as e:
        print(f"  ⚠️  Drop warning: {e}")
    
    # Create FTS5 table with correct configuration
    cursor.execute('''
        CREATE VIRTUAL TABLE reviews_fts USING fts5(
            review_text,
            app_name
        )
    ''')
    print("  ✅ Created new FTS5 table")
    
    # Populate FTS5 table from reviews and apps
    cursor.execute('''
        INSERT INTO reviews_fts (rowid, review_text, app_name)
        SELECT r.id, r.review, a.name
        FROM reviews r
        JOIN apps a ON r.appid = a.appid
    ''')
    
    rows_inserted = cursor.rowcount
    print(f"  ✅ Populated FTS5 with {rows_inserted} rows")
    
    # Test the fixed FTS5
    cursor.execute("SELECT COUNT(*) FROM reviews_fts WHERE reviews_fts MATCH 'fun'")
    test_count = cursor.fetchone()[0]
    print(f"  🧪 Test search for 'fun': {test_count} results")
    
    conn.commit()
    conn.close()
    
    print("\n✅ FTS5 table fixed successfully!")

if __name__ == "__main__":
    if diagnose_fts5_issue():
        fix_fts5_table()
        print("\n🎉 Database is ready for API testing!")
