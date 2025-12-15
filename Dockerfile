# ⚠️ Replace:
# PROJECT_ENTRY_POINT:app → e.g., myapp.main:app









# =========================
# Builder stage
# =========================
FROM python:3.12-slim AS builder

ENV PYTHONUNBUFFERED=1
ENV APP_HOME=/app

WORKDIR $APP_HOME

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install in /install
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# Copy project source code
COPY . .

# =========================
# Final stage
# =========================
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV APP_HOME=/app

WORKDIR $APP_HOME

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /install /usr/local
COPY --from=builder $APP_HOME $APP_HOME



# Expose FastAPI port
EXPOSE 8000


# Run Gunicorn with Uvicorn workers using external config

# CMD ["gunicorn", "--config", "gunicorn_config.py", "com.mhire.app.main:app"]
CMD ["gunicorn", "com.mhire.app.main:app", "-c", "gunicorn_config.py"]