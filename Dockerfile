# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# Build the local TF-IDF index at build time (won't fail the build if docs are empty)
RUN python rag/ingest.py || true

# Defaults (safe): dry-run, no approvals
ENV APPROVE=false

# Expose API (FastAPI)
EXPOSE 8000
CMD ["uvicorn", "server_fastapi:app", "--host", "0.0.0.0", "--port", "8000"]
