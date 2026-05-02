from fastapi import FastAPI
import requests
import chromadb
import json
import os

app = FastAPI()

VECTOR_DB_URL = os.environ.get('VECTOR_DB_URL', 'http://vectordb:8000')
LLM_URL = os.environ.get('LLM_URL', 'http://llm:11434')

client = chromadb.HttpClient(host="vectordb", port=8000)
collection = client.get_or_create_collection(name="chunks")


def embed_text(text):
    payload = {
        "model": "nomic-embed-text",
        "prompt": text
    }
    response = requests.post(f"{LLM_URL}/api/embeddings", json=payload)
    return response.json()["embedding"]


@app.get("/capabilities")
def get_capabilities():
    print("MCP received request for capabilities")
    return [
        {
            "name": "findChunks",
            "description": "Allows loading text chunks by keywords from a bucket of text files",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "search_query": {
                        "type": "string",
                        "description": "a question about the things to search for"
                    }
                },
                "required": ["search_query"]
            }
        },
        {
            "name": "sendMail",
            "description": "Allows sending emails",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "to": {"type": "string"},
                    "subject": {"type": "string"},
                    "body": {"type": "string"}
                },
                "required": ["to", "subject", "body"]
            }
        }
    ]


@app.post("/execute")
def execute_tool(data: dict):
    print("MCP received request to execute tool:", data)

    tool = data["tool"]
    args = data["args"]

    if tool == "findChunks":
        try:
            search_query = args["search_query"]
            query_embedding = embed_text(search_query)
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=5
            )
            output = []

            # ChromaDB returns results as lists of lists (one per list per embedding ... so we only need one)
            documents = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]

            if not documents:
                return output

            for chunk_content, metadata in zip(documents, metadatas):
                if metadata and "fileUrl" in metadata:
                    output.append(
                        {"file": metadata["fileUrl"], "chunkContent": chunk_content})

            return output
        except Exception as e:
            return {"error": f"Failed to find chunks: {str(e)}"}

    elif tool == "sendMail":
        print(
            f"Simulating sending email to: {args['to']}, subject: {args['subject']}, body: {args['body']}")
        return f"Mail sent: {args}"

    else:
        raise ValueError(f"No such tool: '{tool}'")
