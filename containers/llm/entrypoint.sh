#!/bin/bash

# Pull the model if not already present
ollama pull llama3

# Start the server
exec ollama serve