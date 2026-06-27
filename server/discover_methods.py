"""
Discover Qdrant search methods
"""
from qdrant_client import QdrantClient
import inspect

try:
    client = QdrantClient(host='localhost', port=6333)
    print("ALL methods in QdrantClient:")
    all_methods = [attr for attr in dir(client) if not attr.startswith('_')]
    for m in sorted(all_methods):
        print(f"  • {m}")

except Exception as e:
    print(f"Error: {e}")
