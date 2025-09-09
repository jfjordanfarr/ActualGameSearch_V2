#!/usr/bin/env python3
"""
Quick SQLite to SQL export for D1 testing
Exports our phase2_hybrid_search.db to a SQL file that D1 can import
"""

import sqlite3
import sys
from pathlib import Path

def export_sqlite_to_sql(db_path, output_path):
    """Export SQLite database to SQL text format"""
    print(f"📦 Exporting {db_path} to {output_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("-- ActualGameSearch Phase 2 Database Export\n")
        f.write("-- Generated for Cloudflare D1 import\n\n")
        
        # Get all tables (skip SQLite system tables)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row[0] for row in cursor.fetchall()]
        
        for table_name in tables:
            print(f"  📄 Exporting table: {table_name}")
            
            # Get CREATE TABLE statement
            cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            create_sql = cursor.fetchone()[0]
            f.write(f"{create_sql};\n\n")
            
            # Count rows for progress
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            
            if row_count > 0:
                f.write(f"-- Data for {table_name} ({row_count} rows)\n")
                
                # Get column names
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [col[1] for col in cursor.fetchall()]
                
                # Export data in batches to avoid memory issues
                batch_size = 100
                for offset in range(0, row_count, batch_size):
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT {batch_size} OFFSET {offset}")
                    rows = cursor.fetchall()
                    
                    for row in rows:
                        values = []
                        for val in row:
                            if val is None:
                                values.append('NULL')
                            elif isinstance(val, str):
                                # Escape single quotes and handle special characters
                                escaped = val.replace("'", "''").replace('\n', '\\n').replace('\r', '\\r')
                                values.append(f"'{escaped}'")
                            elif isinstance(val, (int, float)):
                                values.append(str(val))
                            else:
                                values.append(f"'{str(val)}'")
                        
                        values_str = ', '.join(values)
                        f.write(f"INSERT INTO {table_name} VALUES ({values_str});\n")
                
                f.write("\n")
    
    conn.close()
    print(f"✅ Export complete: {output_path}")

if __name__ == "__main__":
    db_path = Path("pipeline/data/phase2_hybrid_search.db")
    output_path = Path("temp-scripts/phase2_export.sql")
    
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        sys.exit(1)
    
    export_sqlite_to_sql(db_path, output_path)
    print(f"🚀 Ready to import with: npx wrangler d1 execute ags-local-test --file=temp-scripts/phase2_export.sql --local")
