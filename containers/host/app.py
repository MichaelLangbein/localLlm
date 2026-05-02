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
    print("Host sending messages to LLM:", messages)

    payload = {
        "model": "llama3",
        "messages": messages,
        "stream": False
    }

    try:
        response = requests.post(
            f"{LLM_URL}/api/chat", json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("message", {}).get("content", "No content in response")
    except requests.RequestException as e:
        return f"Error calling LLM: {str(e)}"
    except json.JSONDecodeError:
        return "Error: Invalid JSON response from LLM"


def call_mcp_execute(tool, args):
    payload = {
        "tool": tool,
        "args": args
    }
    response = requests.post(f"{MCP_URL}/execute", json=payload)
    return response.json()


@app.post("/query")
def query_endpoint(data: dict):
    print("Host received query:", data)
    query = data["query"]

    mcp_calls_available = get_mcp_capabilities()

    messages = [{
        "role": "system",
        "content": f"You are the 'assistant', helping the 'user'. Tools available: {json.dumps(mcp_calls_available)}. If you want to call an MCP tool, answer with [TOOL_CALL]{{\"tool\": \"<toolName>\", \"args\": <toolArgs>}}[/TOOL_CALL]. Output only valid JSON between the TOOL_CALL markers."
    }, {
        "role": "user",
        "content": query
    }]

    loop_ongoing = True
    nr_requests = 0

    while loop_ongoing and nr_requests < 4:
        print("Host calling llm ...")
        answer = call_llm(messages)
        print("... llm call yielded answer:", repr(answer))

        if match := mcp_regex.search(answer):
            tool_call_text = match.group(0)
            tool_call = json.loads(match.group(1))
            tool = tool_call["tool"]
            args = tool_call["args"]

            print("Host calling MCP tool:", tool, "with args:", args)
            mcp_results = call_mcp_execute(tool, args)

            messages.append({"role": "assistant", "content": tool_call_text})
            # Add the tool results as a *user* message with readable text (would usually be `role: tool`, but llama3 doesn't know about that role)
            tool_result_text = f"Tool '{tool}' executed with args {json.dumps(args)}. Results: {json.dumps(mcp_results, indent=2)}"
            messages.append({
                "role": "user",
                "content": tool_result_text
            })

            nr_requests += 1
            if nr_requests >= 4:
                messages.append({
                    "role": "system",
                    "content": "The assistant may no longer call MCP. Answer directly to the user in text now."
                })
        else:
            # No tool call, this is the final answer
            loop_ongoing = False

    print("Host final answer:", answer)
    return {"answer": answer}
