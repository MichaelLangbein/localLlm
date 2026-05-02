#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Usage: $0 \"your query here\""
    exit 1
fi

QUERY="$1"

curl -X POST http://localhost:5003/query \
     -H "Content-Type: application/json" \
     -d "{\"query\": \"$QUERY\"}"