#!/bin/bash

cd containers
docker-compose build
docker-compose up -d

# Wait for services to start
echo "Waiting for services to start..."
sleep 30

# Upload dummy files
echo "Uploading dummy files..."
for file in ../../data/*.txt; do
    if [ -f "$file" ]; then
        echo "Uploading $file"
        curl -X POST http://localhost:5002/upload -F "file=@$file"
    fi
done

echo "Initialization complete. Containers are running and files are uploaded."