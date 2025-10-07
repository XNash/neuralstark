#!/usr/bin/env python3
import sys
sys.path.insert(0, '/app')
from backend.config import settings
import chromadb

client = chromadb.PersistentClient(
    path=settings.CHROMA_DB_PATH,
    settings=chromadb.Settings(
        anonymized_telemetry=False,
        allow_reset=True,
        is_persistent=True
    )
)

collections = client.list_collections()
print(f"Collections in ChromaDB: {len(collections)}")
for coll in collections:
    print(f"  - {coll.name}: {coll.count()} documents")
