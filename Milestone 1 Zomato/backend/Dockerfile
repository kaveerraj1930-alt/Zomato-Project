# Backend Dockerfile — build context is project root
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for datasets/pandas
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements first for layer caching
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy entire project root so backend can import models/, data/, phase3/, phase4/, config/
COPY . /app/

# Ensure project root is on PYTHONPATH for absolute imports
ENV PYTHONPATH=/app

# Expose FastAPI port
EXPOSE 8000

# Run uvicorn
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
