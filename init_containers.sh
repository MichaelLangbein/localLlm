#!/bin/bash

cd containers
docker-compose build
docker-compose up -d


echo "Initialization complete. Containers are running."
echo "Don't forget to upload files to the 'files' directory for testing the findChunks tool."
echo "You can run './test.sh' to execute test queries against the host server."