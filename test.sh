
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

# curl -X POST http://localhost:5001/execute -H "Content-Type: application/json" -d '{
#   "tool": "findChunks",
#   "args": {
#     "search_query": "latest news on renewable energy"
#   }
# }'


#curl http://localhost:11434/api/chat -d '{
#  "model": "llama3",
#  "stream": false,
#  "messages": [
#        {
#            "role": "system",
#            "content": "Tools available: [{\"name\": \"findChunks\", \"description\": \"Allows loading text chunks by keywords from a bucket of text files\", \"inputSchema\": {\"type\": \"object\", \"properties\": {\"search_query\": {\"type\": \"string\", \"description\": \"a question about the things to search for\"}}, \"required\": [\"search_query\"]}}, {\"name\": \"sendMail\", \"description\": \"Allows sending emails\", \"inputSchema\": {\"type\": \"object\", \"properties\": {\"to\": {\"type\": \"string\"}, \"subject\": {\"type\": \"string\"}, \"body\": {\"type\": \"string\"}}, \"required\": [\"to\", \"subject\", \"body\"]}}]. If you want to call an MCP tool, answer with [TOOL_CALL]{\"tool\": \"<toolName>\", \"args\": <toolArgs>}[/TOOL_CALL]. Output only valid JSON between the TOOL_CALL markers."
#        },
#        { 
#            "role": "user", 
#            "content": "what does my org know about dogs?" 
#        },
#        {
#            "role": "assistant",
#            "content": "[TOOL_CALL]{ \"tool\": \"findChunks\", \"args\": { \"search_query\": \"dogs\" } }[/TOOL_CALL]"
#        },
#        {
#            "role": "user",
#            "content": "Tool 'findChunks' executed with args {\"search_query\": \"dogs\"}. Results: [\n  {\n    \"file\": \"/files/dog_breeds.txt\",\n    \"chunkContent\": \"Dogs have been human companions for thousands of years, evolving from wolves through domestication. There are over 300 recognized breeds, each with unique characteristics. Labrador Retrievers are known for their friendly nature and intelligence, often used as service animals. German Shepherds excel in police and military work due to their strength and trainability. Poodles, despite their fancy appearance, are highly intelligent and excel in obedience trials. The bond between dogs and humans is evident in their ability to understand emotions and provide comfort.\"\n  }\n]"
#        }
#  ]
#}'


./query_host.sh "what does my org know about dogs?"
