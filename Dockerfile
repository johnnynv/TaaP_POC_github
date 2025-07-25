# TaaP POC GitHub - Dockerfile for containerized testing

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create reports directory
RUN mkdir -p reports htmlcov

# Set up proper permissions
RUN chmod +x /app

# Create non-root user for security
RUN useradd -m -u 1000 testuser && \
    chown -R testuser:testuser /app
USER testuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default command
CMD ["pytest", "--cov=src", "--cov-report=html", "--html=reports/report.html", "--self-contained-html"]

# Labels for metadata
LABEL maintainer="TaaP POC Team"
LABEL version="1.0.0"
LABEL description="TaaP POC GitHub - Cloud Native Testing Platform" 