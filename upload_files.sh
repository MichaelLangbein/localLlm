#!/bin/bash

# Upload dummy files
echo "Uploading dummy files..."
for file in ./data/*.txt; do
    if [ -f "$file" ]; then
        echo "Uploading $file"
        curl -X POST http://localhost:5002/upload -F "file=@$file"
    fi
done

echo "... done"