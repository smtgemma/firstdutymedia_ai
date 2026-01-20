# Use Python slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for Tesseract OCR
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    libtesseract-dev \
    # Add more languages if needed:
    # tesseract-ocr-ben \
    # tesseract-ocr-ara \
    build-essential \
    libjpeg-dev \
    libtiff-dev \
    libgif-dev \
    gcc \
    musl-dev \
    net-tools \
    && rm -rf /var/lib/apt/lists/*
    

# Verify Tesseract installation
RUN tesseract --version

# Copy requirements file
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app/

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run the application
CMD ["uvicorn", "com.mhire.app.main:app", "--host", "0.0.0.0", "--port", "8000"]