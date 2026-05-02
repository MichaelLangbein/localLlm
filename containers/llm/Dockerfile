FROM ollama/ollama:latest


RUN apt-get update && apt-get install curl -y
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]