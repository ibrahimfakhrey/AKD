# ─── Build Stage ─────────────────────────────────────────────
FROM python:3.13-slim AS base

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir psycopg2-binary gunicorn

# Application code
COPY . .

# Create uploads directory
RUN mkdir -p /app/uploads

# Expose port
EXPOSE 5000

# Environment defaults
ENV FLASK_CONFIG=production
ENV FLASK_APP=wsgi.py

# ─── Production ──────────────────────────────────────────────
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "wsgi:app"]
