#!/bin/bash

cd containers
docker-compose build
docker-compose up -d


echo "Initialization complete. Containers are running"