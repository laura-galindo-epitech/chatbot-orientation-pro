import chromadb

chroma_client = chromadb.PersistentClient(path="./chroma_db")

print("✅ ChromaDB is running!")
print("Available collections:", chroma_client.list_collections())

# Keep the script running
import time
while True:
    time.sleep(100)
