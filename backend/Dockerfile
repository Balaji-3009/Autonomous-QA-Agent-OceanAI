FROM python:3.11-slim

# Prevent Python from buffering stdout (useful for logs)
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies for ChromaDB
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ make libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create uploads folder
RUN mkdir -p uploads

# Expose port for Cloud Run
ENV PORT=8080
EXPOSE 8080

# Start FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
