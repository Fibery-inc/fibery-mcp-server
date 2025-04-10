# Generated by https://smithery.ai. See: https://smithery.ai/docs/config#dockerfile
FROM python:3.10-slim

WORKDIR /app

# Copy project files
COPY pyproject.toml ./
COPY README.md ./
COPY src/ ./src/

# Install dependencies and the package itself
RUN pip install --upgrade pip \
    && pip install --ignore-installed .

# Expose a port if needed, though MCP runs over stdio by default

ENTRYPOINT ["fibery-mcp-server"]
