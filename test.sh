
# testing that llm is present and working

# curl http://localhost:11434/api/chat -d '{
#   "model": "llama3",
#   "stream": false,
#   "messages": [
#     {
#       "role": "user",
#       "content": "why is the sky blue?"
#     }
#   ]
# }'


# testing that embedding works


# curl http://localhost:11434/api/embeddings -d '{
#   "model": "llama3",
#   "prompt": "dogs AND renewables"
# }'


# testing mcp server

# curl http://localhost:5001/capabilities

curl -X POST http://localhost:5001/execute -H "Content-Type: application/json" -d '{
  "tool": "findChunks",
  "args": {
    "search_query": "latest news on renewable energy"
  }
}'


