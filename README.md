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
  - based on ollama, using local 8-bit model
- mcp server <-- `mcpService`
  - exposes fake email server
- bucket for uploading text files
  - ingestion script
- vector db <-- `vectorDbService`

## Ingestor pseudocode

```python

def onFileUpload(file):

    fileContents = read(file)
    fileUrl = saveFileLocally(file)
    embedding = llmService.embed(fileContents)
    vectorDbService.upload(embedding, fileUrl)

```

## Host pseudocode

```python

def host(query):

    keywords = llmService.query(f"""
        Please list the most important keywords in this user query. Answer in JSON.
        Query:
        {query}
    """)

    backgroundInformation = vectorDbService.query(keywords)

    mcpCallsAvailable = mcpService.getCapabilities()

    answer = llmService.query(f"""
        Here is a user query:
        {query}
        Try to answer it given the following background information:
        {backgroundInformation}
        You can also call any of these MCP tools if you need to.
        {mcpCallsAvailable}
    """)

    while mcpRegex.matches(answer):

        results = mcpService.execute(answer)

        backgroundInformation += results

        answer = llmService.query(f"""
            Here is a user query:
            {query}
            Try to answer it given the following background information:
            {backgroundInformation}
            You can also call any of these MCP tools if you need to.
            {mcpCallsAvailable}
        """)

    return answer



```
