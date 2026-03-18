FROM python:3.12-slim

LABEL maintainer="Lasseigne Lab"
LABEL description="ACMG/AMP Variant Classification Advisor"

WORKDIR /app

# Install runtime dependencies only
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy source code
COPY src/ src/

# Create non-root user
RUN adduser --disabled-password --gecos "" appuser
USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/')" || exit 1

# Run with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "src.variant_classifier.web.app:app"]
