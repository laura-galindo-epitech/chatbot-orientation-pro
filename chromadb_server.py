from fastapi import FastAPI
from pydantic import BaseModel
import chromadb

# Initialize FastAPI
app = FastAPI()

# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Define a test route
@app.get("/")
def read_root():
    return {"message": "ChromaDB server is running!"}

# Endpoint to list collections
@app.get("/collections")
def list_collections():
    collections = chroma_client.list_collections()
    return {"collections": [col.name for col in collections]}

# Define data model for adding collections
class CollectionRequest(BaseModel):
    name: str

# Endpoint to add a new collection
@app.post("/collections")
def create_collection(request: CollectionRequest):
    collection = chroma_client.get_or_create_collection(name=request.name)
    return {"message": f"Collection '{request.name}' created successfully!"}

# Run this script with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)