FROM python:3.12-slim AS base

# System deps for Tesseract OCR and PostgreSQL client
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r savdhaan && useradd -r -g savdhaan -d /app -s /sbin/nologin savdhaan

WORKDIR /app

# Install Python dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e ".[dev]" 2>/dev/null || pip install --no-cache-dir .

# Copy source code
COPY . .

# Install the project
RUN pip install --no-cache-dir -e .

# Switch to non-root user
USER savdhaan

EXPOSE 8000

CMD ["gunicorn", "src.main:app", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--workers", "2", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--access-logfile", "-"]
