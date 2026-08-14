FROM python:3.11-alpine

LABEL maintainer="DevSecOps Engineering"
LABEL description="Hardened Flask Application for Security Pipeline"

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip "setuptools>=78.1.1" wheel && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN addgroup -S appgroup && adduser -S appuser -G appgroup && \
    chown -R appuser:appgroup /app

USER appuser

EXPOSE 5000

CMD ["python", "app.py"]