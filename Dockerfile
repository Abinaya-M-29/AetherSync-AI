# Stage 1: Build the React frontend
FROM node:25.9.0-alpine AS frontend-builder
WORKDIR /app/frontend
COPY src/frontend/package*.json ./
RUN npm install
COPY src/frontend ./
RUN npm run build

# Stage 2: Build the FastAPI backend
FROM python:3.12-slim
WORKDIR /app

# Install system dependencies (gcc and sqlite3 for the database)
RUN apt-get update && apt-get install -y gcc sqlite3 && rm -rf /var/lib/apt/lists/*

# Copy backend dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and directories
# Copy source code and directories (which includes secrets/ and database/)
COPY src/ ./src/

# Copy built frontend from Stage 1 into the correct path inside src/
COPY --from=frontend-builder /app/frontend/dist /app/src/frontend/dist

# Switch working directory to src/ so relative paths like "secrets/" work!
WORKDIR /app/src

# Expose port (Cloud Run sets the PORT env var dynamically)
EXPOSE 8080

# Run FastMCP server in background on port 8081, then run uvicorn on the container's designated port
CMD ["sh", "-c", "python mcp_server/server.py & uvicorn backend.api.app:app --host 0.0.0.0 --port ${PORT:-8080}"]
