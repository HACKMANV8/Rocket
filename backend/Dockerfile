# Use lightweight Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip first
RUN python -m pip install --upgrade pip

# Copy requirements
COPY requirements.txt .

# Install all dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# ✅ Download SentenceTransformer model safely
RUN python -c "from sentence_transformers import SentenceTransformer; \
print('📥 Downloading embedding model...'); \
SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2'); \
print('✅ Model download complete.')"

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/chroma_data /app/models_cache /app/data

# Set environment variables
ENV TRANSFORMERS_CACHE=/app/models_cache
ENV HUGGINGFACE_HUB_CACHE=/app/models_cache
ENV CHROMA_PERSIST_DIR=/app/chroma_data
ENV PYTHONUNBUFFERED=1

# Expose Flask port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Run Flask app with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]
