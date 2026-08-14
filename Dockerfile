FROM python:3.11-slim-bookworm

LABEL maintainer="DevSecOps Engineering"

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip "setuptools>=78.1.1" wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir --upgrade "msgpack>=1.2.1"

COPY . .

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

RUN find / -type f \( -name "*.sbom" -o -name "*.spdx" -o -name "*.cdx" \) 2>/dev/null


EXPOSE 5000

CMD ["python", "app.py"]