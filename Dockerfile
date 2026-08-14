FROM python:3.11-alpine

LABEL maintainer="DevSecOps Engineering"
LABEL description="Hardened Flask Application for Security Pipeline"

WORKDIR /app

COPY requirements.txt .

# Remove old  setuptools/pip ruins and install current version
RUN rm -rf /usr/local/lib/python3.11/site-packages/setuptools* && \
    pip install --no-cache-dir --upgrade pip "setuptools>=78.1.1" wheel && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN addgroup -S appgroup && adduser -S appuser -G appgroup && \
    chown -R appuser:appgroup /app

USER appuser

EXPOSE 5000

CMD ["python", "app.py"]