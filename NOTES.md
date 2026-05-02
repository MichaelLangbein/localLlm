## Scripts

- `./init_containers.sh`: Build and start the Docker containers, then upload dummy files
- `./run_containers.sh`: Start the containers in detached mode (if not already running)
- `./upload_file.sh <file_path>`: Upload a file to the fileBucket
- `./query_host.sh "your query"`: Send a query to the host

## URLs

- File upload: http://localhost:5002/upload
- Host query: http://localhost:5003/query (POST with {"query": "your question"})

## Dummy Data

Dummy text files are in `data/`:

- ai_history.txt
- dog_breeds.txt
- renewable_energy.txt

Example workflow:

1. ./init_containers.sh (builds, starts containers, uploads dummy files)
2. ./query_host.sh "What are some dog breeds?"
