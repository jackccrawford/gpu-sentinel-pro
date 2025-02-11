FROM python:3.10-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ backend/
COPY src/ src/

# Set environment variables
ENV PYTHONPATH=/app

# Run both collector and API server
CMD ["sh", "-c", "python -m src.collector.collector & python -m backend.src.service.app"]
