FROM python:3.12-slim

LABEL maintainer="Lasseigne Lab"
LABEL description="ACMG/AMP Variant Classification Advisor"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY tests/ tests/

EXPOSE 8080

# Default: run the web app
CMD ["python", "-m", "flask", "--app", "src.variant_classifier.web.app:app", "run", "--host", "0.0.0.0", "--port", "8080"]
