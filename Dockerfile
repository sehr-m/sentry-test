FROM python:3.11-slim

WORKDIR /app

# Install dependencies first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

# Expose port
EXPOSE 5000

# Environment variables (set these when running the container)
ENV SENTRY_DSN=""
ENV SENTRY_ENVIRONMENT="docker"
ENV SENTRY_RELEASE="sentry-test@1.0.0"
ENV PORT=5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

CMD [ "python", "-u", "hello.py" ]
