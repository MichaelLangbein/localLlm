# Local LLM

## Objective

To learn the basics of: locally hosted LLMs, RAG, and MCP.
This is for educational purpose only. Performance is irrelevant, readability is important.
This is to learn about concepts, not about optimizing.

- locally hosted LLMs

- MCP:
  - llm is allowed to answer with MCP calls instead of text
  - For this, the host first lists all allowed MCP functions and their arguments to the model
  - It tells the llm that it is allowed to call those MCP functions instead of answering in text

- RAG:
  - Request comes in at host.
  - LLM decides to look for more information via MCP.
  - Loaded information is added to query context
  - llm answers with the background knowledge of the newly loaded context information

## Architecture (all docker containers)

- host
  - interface between human and other buckets
- llm <-- `llmService`
  - based on ollama llama3 8-bit model
- mcp server <-- `mcpService`
  - exposes fake email server
  - exposes reading chunks from text file bucket
- bucket for uploading text files <-- `bucketService`
  - ingestion script: writes embeddings of file chunks into vector db
- vector db <-- `vectorDbService`
  - contains vectors for the most important keywords in text-file-chunks
  - the embedded vector for "dog" will be similar to that for "retriever" ... thus making search much more robust

## Ingestor pseudocode

```python

def onFileUpload(file):

    fileContents = read(file)
    fileUrl = saveFileLocally(file)

    for chunkNr, chunk in splitContents(fileContents, words=1_000):
        embedding = llmService.embed(chunk)
        vectorDbService.upload(embedding, fileUrl, chunkNr)

```

## MCP server pseudocode

```python
def getCapabilities():
    return [{
        "name": "findChunks",
        "description": "Allows loading text chunks by keywords from a bucket of text files",
        "inputSchema": {
            "name": "search_query",
            "type": "string",
            "description": "a question about the things to search for"
        }
    }, {
        "name": "sendMail",
        "description": "Allows sending emails",
        "inputSchema": {
            "type": "object",
            "properties": {
                "to": {"type": "string"},
                "subject": {"type": "string"},
                "body": {"type": "string"}
            }
        }
    }]


def execute(tool, *args):

    if tool == "findChunks":
        output = []
        for fileUrl, chunkNr in vectorDbService.similarity_search(args):
            chunkContent = bucketService.loadFileChunk(fileUrl, chunkNr)
            output.append({"file": fileUrl, "chunkContent": chunkContent})
        return output

    elif tool == "sendMail":
        return f"Mail sent: {args}"

    else:
        raise Error(f"No such tool: '{tool}'")

```

## Host pseudocode

```python

mcpRegex = /[TOOL_CALL](.*)[/TOOL_CALL]/

def host(query):

    mcpCallsAvailable = mcpService.getCapabilities()

    messages = [
        {"role": "system", "content": f"Tools available: {mcpCallsAvailable}. If you want to call an MCP tool, answer with [TOOL_CALL]{'tool': <toolName>, 'args': <toolArgs>}[/TOOL_CALL]. Output only valid JSON between the TOOL_CALL markers."},
        {"role": "user", "content": query}
    ]

    loopOngoing = True
    nrRequests = 0

    while loopOngoing:

        answer = llmService.query(messages)

        if match := mcpRegex.match(answer):

            mcpResults = mcpService.execute(match["tool"], match["args"])
            messages.append({"role": "assistant", "content": answer})
            messages.append({"role": "tool", "content": mcpResults})

            nrRequests += 1
            if nrRequests >= 4:
                messages.append({"role": "system", "content": "The assistant may no longer call MCP. Answer directly to the user in text now."})

        else:
            loopOngoing = False

    return answer



```
