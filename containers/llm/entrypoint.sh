#!/bin/bash

echo "Starting Ollama server and pulling model..."

# 1. Start the Ollama server in the background
ollama serve &

# 2. Wait for the server to respond (health check)
echo "Waiting for Ollama server to start..."
while ! curl -s localhost:11434/api/tags > /dev/null; do
    sleep 1
done

# 3. Pull the models now that the server is up
echo "Pulling llama3..."
ollama pull llama3

echo "Pulling nomic-embed-text for embeddings..."
ollama pull nomic-embed-text

# 4. Bring the server process to the foreground
wait