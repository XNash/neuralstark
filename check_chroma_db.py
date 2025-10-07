#!/usr/bin/env python3
import sqlite3

db_path = "/app/chroma_db/chroma.sqlite3"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print(f"Tables in database: {[t[0] for t in tables]}")
print()

# Check collections table
cursor.execute("SELECT * FROM collections;")
collections = cursor.fetchall()
print(f"Collections: {len(collections)}")
for coll in collections:
    print(f"  {coll}")
print()

# Check embeddings table
try:
    cursor.execute("SELECT COUNT(*) FROM embeddings;")
    count = cursor.fetchone()[0]
    print(f"Total embeddings: {count}")
    
    if count > 0:
        cursor.execute("SELECT * FROM embeddings LIMIT 3;")
        samples = cursor.fetchall()
        print(f"Sample embeddings (first 3): {len(samples)} rows")
except Exception as e:
    print(f"Error checking embeddings: {e}")

conn.close()
