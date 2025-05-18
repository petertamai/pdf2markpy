FROM python:3.10-slim

WORKDIR /app

# Add custom label for identification
LABEL maintainer="Peter Tam <pt@petertam.pro>"
LABEL description="PDF to Markdown Conversion API Service"
LABEL version="1.0"

# Install build dependencies and cleanup in a single RUN to reduce image size
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create temp directory for uploads
RUN mkdir -p /tmp/pdf2md && \
    chmod 777 /tmp/pdf2md

# Copy application code
COPY pdf2md.py .

# Create a non-root user for security
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set environment variables
ENV PORT=3000
ENV PYTHONUNBUFFERED=1
ENV DEBUG=False

# Expose the port
EXPOSE 3000

# Use Gunicorn as the production WSGI server
CMD ["gunicorn", "--bind", "0.0.0.0:3000", "--workers", "4", "--access-logfile", "-", "--error-logfile", "-", "--timeout", "120", "pdf2md:app"]