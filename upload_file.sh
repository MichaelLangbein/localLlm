#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Usage: $0 <file_path>"
    exit 1
fi

FILE_PATH="$1"

curl -X POST http://localhost:5002/upload \
     -F "file=@$FILE_PATH"