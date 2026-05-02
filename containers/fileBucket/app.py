from fastapi import FastAPI, UploadFile, File
import os
import json
import requests
import chromadb
from typing import Dict

app = FastAPI()

LLM_URL = os.environ.get('LLM_URL', 'http://llm:11434')
VECTOR_DB_URL = os.environ.get('VECTOR_DB_URL', 'http://vectordb:8000')

FILES_DIR = "/app/files"
CHUNKS_FILE = "/app/chunks.json"

if not os.path.exists(FILES_DIR):
    os.makedirs(FILES_DIR)

# Load chunks
if os.path.exists(CHUNKS_FILE):
    with open(CHUNKS_FILE, 'r') as f:
        chunks: Dict[str, str] = json.load(f)
else:
    chunks = {}

client = chromadb.HttpClient(host="vectordb", port=8000)
collection = client.get_or_create_collection(name="chunks")


def embed_text(text):
    payload = {
        "model": "llama3",
        "prompt": text
    }
    response = requests.post(f"{LLM_URL}/api/embeddings", json=payload)
    return response.json()["embedding"]


def split_into_chunks(text, words_per_chunk=1000):
    words = text.split()
    chunks = []
    for i in range(0, len(words), words_per_chunk):
        chunk = ' '.join(words[i:i+words_per_chunk])
        chunks.append(chunk)
    return chunks


@app.post("/upload")
def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(FILES_DIR, file.filename)
    with open(file_path, 'wb') as f:
        f.write(file.file.read())

    file_url = f"/files/{file.filename}"

    with open(file_path, 'r') as f:
        file_contents = f.read()

    chunk_list = split_into_chunks(file_contents)

    for chunk_nr, chunk in enumerate(chunk_list):
        embedding = embed_text(chunk)
        collection.add(
            embeddings=[embedding],
            documents=[chunk],
            metadatas=[{"fileUrl": file_url, "chunkNr": chunk_nr}],
            ids=[f"{file_url}_{chunk_nr}"]
        )
        chunks[f"{file_url}_{chunk_nr}"] = chunk

    # Save chunks
    with open(CHUNKS_FILE, 'w') as f:
        json.dump(chunks, f)

    return {"message": "File uploaded and ingested"}


@app.get("/get_chunk")
def get_chunk(fileUrl: str, chunkNr: int):
    key = f"{fileUrl}_{chunkNr}"
    if key in chunks:
        return {"chunk": chunks[key]}
    else:
        return {"error": "Chunk not found"}
