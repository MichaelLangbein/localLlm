# Local LLM

## Objective

To learn the basics of: locally hosted LLMs, RAG, and MCP.
This is for educational purpose only. Performance is irrelevant, readability is important.
This is to learn about concepts, not about optimizing.

- locally hosted LLMs

- RAG:
  - Request comes in at host. Host first asks llm to list keywords from the query.
  - llm lists important keywords from query
  - host loads relevant information pertaining those keywords from bucket container into query context
  - llm answers with the background knowledge of the newly loaded context information

- MCP:
  - llm is allowed to answer with MCP calls instead of text
  - For this, the host first lists all allowed MCP functions and their arguments to the model
  - It tells the llm that it is allowed to call those MCP functions instead of answering in text

RAG will be implemented by adding content from a bucket full of textfiles.
MCP will be simulated by exposing to the AI a fake email-server where it is being made to believe that it can send email.

## Architecture (all docker containers)

- host
  - interface between human and other buckets
- llm <-- `llmService`
  - based on ollama llama3 8-bit model
- mcp server <-- `mcpService`
  - exposes fake email server
- bucket for uploading text files <-- `bucketService`
  - ingestion script
- vector db <-- `vectorDbService`

## Ingestor pseudocode

```python

def onFileUpload(file):

    fileContents = read(file)
    fileUrl = saveFileLocally(file)

    for chunkNr, chunk in splitContents(fileContents, words=1_000):
        embedding = llmService.embed(fileContents)
        vectorDbService.upload(embedding, fileUrl, chunkNr)

```

## MCP server pseudocode

```python
def getCapabilities():
    return [{
        "name": "readFiles",
        "description": "Allows loading text chunks by keywords from a bucket of text files",
        "inputSchema": {...}
    }, {
        "name": "sendMail",
        "description": "Allows sending emails",
        "inputSchema": {...}
    }]


def execute(tool, *args):

    if tool == "readFiles":
        fileUrls, chunkNrs = vectorDbService.similarity_search(*args)
        fileContents = bucketService.loadFiles(fileUrls, chunkNrs)
        return fileContents

    elif tool == "sendMail":
        return f"Mail sent: {args}"

    else:
        pass

```

## Host pseudocode

```python

def host(query):

    messages = [
        {"role": "system", "content": f"Tools available: {mcpCallsAvailable}. If you want to call an MCP tool, answer with [CALL:<toolname>(<toolArg>*)]"},
        {"role": "user", "content": query}
    ]

    # should return:
    # -- MCP to read from vectorDb
    # -- MCP to write emails
    mcpCallsAvailable = mcpService.getCapabilities()

    loopOngoing = True

    while loopOngoing:

        answer = llmService.query(messages)

        if mcpRegex.match(answer):

            mcpResults = mcpService.execute(answer)
            messages.append({"role": "assistant", "content": answer})
            messages.append({"role": "tool", "content": mcpResults})

        else:
            loopOngoing = False

    return answer



```
