#!/usr/bin/env python3
"""
Phase 2 Data Migration: Phase 1 → Hybrid Search Database
Migrate Phase 1 embeddings and Steam data into FTS5 + vector hybrid database
"""

import pandas as pd
import sqlite3
import json
from pathlib import Path

# Configuration
DATA_DIR = Path("../data")
PHASE1_DB = DATA_DIR / "phase1_vector_prototype.db"
PHASE2_DB = DATA_DIR / "phase2_hybrid_search.db"

def create_phase2_schema(conn):
    """Create Phase 2 database schema"""
    # Apps table - core Steam game metadata
    conn.execute('''
    CREATE TABLE IF NOT EXISTS apps (
        app_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        short_description TEXT,
        detailed_description TEXT,
        reputation_score REAL DEFAULT 0.0,
        review_count INTEGER DEFAULT 0
    )
    ''')
    
    # Reviews table - game reviews with quality scoring
    conn.execute('''
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        app_id INTEGER,
        review_text TEXT NOT NULL,
        quality_score REAL DEFAULT 0.0,
        word_count INTEGER DEFAULT 0,
        voted_up BOOLEAN DEFAULT FALSE,
        language TEXT DEFAULT 'unknown',
        FOREIGN KEY (app_id) REFERENCES apps (app_id)
    )
    ''')
    
    # FTS5 virtual table for fast lexical search
    conn.execute('''
    CREATE VIRTUAL TABLE IF NOT EXISTS reviews_fts USING fts5(
        review_text,
        content='reviews',
        content_rowid='id'
    )
    ''')
    
    # Review embeddings for semantic search
    conn.execute('''
    CREATE TABLE IF NOT EXISTS review_embeddings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        app_id INTEGER,
        review_text TEXT NOT NULL,
        embedding_json TEXT NOT NULL,
        quality_score REAL DEFAULT 0.0,
        FOREIGN KEY (app_id) REFERENCES apps (app_id)
    )
    ''')
    
    conn.commit()

def migrate_data():
    """Migrate Phase 1 data to Phase 2 hybrid database"""
    print("=== Phase 2 Data Migration ===")
    
    # Load Steam data
    try:
        apps_df = pd.read_feather(DATA_DIR / "resampled_apps.feather")
        reviews_df = pd.read_feather(DATA_DIR / "resampled_reviews.feather")
        print(f"✅ Loaded {len(apps_df)} apps and {len(reviews_df)} reviews")
    except Exception as e:
        print(f"❌ Error loading Steam data: {e}")
        return
    
    # Connect to databases
    phase1_conn = sqlite3.connect(PHASE1_DB)
    phase2_conn = sqlite3.connect(PHASE2_DB)
    
    # Create Phase 2 schema
    print("🗄️ Creating Phase 2 database schema...")
    create_phase2_schema(phase2_conn)
    print("✅ Schema created")
    
    try:
        # Migrate apps data
        print("📦 Migrating apps data...")
        apps_migrated = 0
        
        for _, app in apps_df.iterrows():
            app_id = None
            try:
                # Map column names (resampled data uses different schema)
                app_id = app.get('steam_appid') or app.get('app_id')
                if not app_id:
                    continue
                    
                phase2_conn.execute("""
                    INSERT OR REPLACE INTO apps 
                    (app_id, name, short_description, detailed_description, reputation_score, review_count)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    int(app_id),
                    str(app.get('name', '')),
                    str(app.get('short_description', '')),
                    str(app.get('detailed_description', '') or app.get('about_the_game', '')),
                    0.0,  # Will calculate later
                    0     # Will calculate later
                ))
                apps_migrated += 1
            except Exception as e:
                print(f"Error migrating app {app_id}: {e}")
        
        print(f"✅ Migrated {apps_migrated} apps")
        
        # Migrate reviews data
        print("📝 Migrating reviews data...")
        reviews_migrated = 0
        
        # Calculate quality scores for reviews (from Phase 1 logic)
        def calculate_quality_score(review_row):
            score = 0.0
            review_text = str(review_row.get('review', ''))
            word_count = len(review_text.split())
            
            if 20 <= word_count <= 200:
                score += 10
            elif 10 <= word_count < 20:
                score += 5
            elif word_count > 200:
                score += 8
            
            if word_count > 0:
                score += 1
            if word_count < 5:
                score -= 5
                
            return max(score, 0)
        
        for _, review in reviews_df.iterrows():
            try:
                app_id = review.get('app_id') or review.get('steam_appid')
                if not app_id:
                    continue
                    
                review_text = str(review.get('review', ''))
                quality_score = calculate_quality_score(review)
                
                # Insert into reviews table
                cursor = phase2_conn.execute("""
                    INSERT OR REPLACE INTO reviews 
                    (app_id, review_text, quality_score, word_count, voted_up, language)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    int(app_id),
                    review_text,
                    quality_score,
                    len(review_text.split()),
                    bool(review.get('voted_up', False)),
                    str(review.get('language', 'unknown'))
                ))
                
                review_id = cursor.lastrowid
                
                # Insert into FTS5 for fast text search
                phase2_conn.execute("""
                    INSERT OR REPLACE INTO reviews_fts (rowid, review_text)
                    VALUES (?, ?)
                """, (review_id, review_text))
                
                reviews_migrated += 1
                
            except Exception as e:
                print(f"Error migrating review: {e}")
        
        print(f"✅ Migrated {reviews_migrated} reviews")
        
        # Migrate embeddings from Phase 1
        print("🔗 Migrating embeddings from Phase 1...")
        embeddings_migrated = 0
        
        phase1_cursor = phase1_conn.execute("""
            SELECT appid, review_text, embedding_json, quality_score 
            FROM review_embeddings
        """)
        
        for row in phase1_cursor.fetchall():
            try:
                phase2_conn.execute("""
                    INSERT OR REPLACE INTO review_embeddings 
                    (app_id, review_text, embedding_json, quality_score)
                    VALUES (?, ?, ?, ?)
                """, row)
                embeddings_migrated += 1
            except Exception as e:
                print(f"Error migrating embedding: {e}")
        
        print(f"✅ Migrated {embeddings_migrated} embeddings")
        
        # Commit all changes
        phase2_conn.commit()
        
        # Verify migration
        print("\n📊 Migration Summary:")
        
        cursor = phase2_conn.execute("SELECT COUNT(*) FROM apps")
        app_count = cursor.fetchone()[0]
        
        cursor = phase2_conn.execute("SELECT COUNT(*) FROM reviews")
        review_count = cursor.fetchone()[0]
        
        cursor = phase2_conn.execute("SELECT COUNT(*) FROM review_embeddings")
        embedding_count = cursor.fetchone()[0]
        
        cursor = phase2_conn.execute("SELECT COUNT(*) FROM reviews_fts")
        fts_count = cursor.fetchone()[0]
        
        print(f"  Apps: {app_count}")
        print(f"  Reviews: {review_count}")
        print(f"  Embeddings: {embedding_count}")
        print(f"  FTS5 entries: {fts_count}")
        
        if embedding_count > 0 and fts_count > 0:
            print("✅ Phase 2 hybrid database ready for testing!")
            return True
        else:
            print("❌ Migration incomplete - missing data")
            return False
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    finally:
        phase1_conn.close()
        phase2_conn.close()

if __name__ == "__main__":
    success = migrate_data()
    if success:
        print("\n🚀 Ready to test hybrid search!")
    else:
        print("\n❌ Migration failed - check data and try again")
