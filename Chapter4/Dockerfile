# Packages the HTTP MCP server (1_rf_http_server.py) as a container.
# Build:  docker build -t rf-mcp-server Chapter4
# Run:    docker run --rm -p 8070:8070 rf-mcp-server
FROM python:3.12-slim

WORKDIR /app
RUN pip install --no-cache-dir "fastmcp>=2.14.3,<3"

COPY 1_rf_http_server.py server.py

# Don't run as root inside the container
RUN useradd --create-home appuser
USER appuser

EXPOSE 8070
CMD ["python", "server.py"]
