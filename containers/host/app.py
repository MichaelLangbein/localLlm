from fastapi import FastAPI
import requests
import json
import re
import os

app = FastAPI()

LLM_URL = os.environ.get('LLM_URL', 'http://llm:11434')
MCP_URL = os.environ.get('MCP_URL', 'http://mcpserver:5001')
VECTOR_DB_URL = os.environ.get('VECTOR_DB_URL', 'http://vectordb:8000')

mcp_regex = re.compile(r'\[TOOL_CALL\](.*)\[/TOOL_CALL\]')


def get_mcp_capabilities():
    response = requests.get(f"{MCP_URL}/capabilities")
    return response.json()


def call_llm(messages):
    payload = {
        "model": "llama3",
        "messages": messages,
        "stream": False
    }
    response = requests.post(f"{LLM_URL}/api/chat", json=payload)
    return response.json()["message"]["content"]


def call_mcp_execute(tool, args):
    payload = {
        "tool": tool,
        "args": args
    }
    response = requests.post(f"{MCP_URL}/execute", json=payload)
    return response.json()


@app.post("/query")
def query_endpoint(data: dict):
    query = data["query"]

    mcp_calls_available = get_mcp_capabilities()

    messages = [
        {"role": "system",
            "content": f"Tools available: {json.dumps(mcp_calls_available)}. If you want to call an MCP tool, answer with [TOOL_CALL]{{\"tool\": \"<toolName>\", \"args\": <toolArgs>}}[/TOOL_CALL]. Output only valid JSON between the TOOL_CALL markers."},
        {"role": "user", "content": query}
    ]

    loop_ongoing = True
    nr_requests = 0

    while loop_ongoing and nr_requests < 4:
        answer = call_llm(messages)

        if match := mcp_regex.search(answer):
            tool_call = json.loads(match.group(1))
            tool = tool_call["tool"]
            args = tool_call["args"]

            mcp_results = call_mcp_execute(tool, args)
            messages.append({"role": "assistant", "content": answer})
            messages.append(
                {"role": "tool", "content": json.dumps(mcp_results)})

            nr_requests += 1
        else:
            loop_ongoing = False

    if nr_requests >= 4:
        messages.append(
            {"role": "system", "content": "The assistant may no longer call MCP. Answer directly to the user in text now."})
        answer = call_llm(messages)

    return {"answer": answer}
