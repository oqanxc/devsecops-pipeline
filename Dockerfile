FROM python:3.11-alpine

LABEL maintainer="DevSecOps Engineering"
LABEL description="Hardened Flask Application for Security Pipeline"

WORKDIR /app

# 1. Pip ve paketleri güncelle, ardından sistemdeki eski ensurepip/dist-info kalıntılarını sil
RUN pip install --no-cache-dir --upgrade pip "setuptools>=78.1.1" "msgpack>=1.2.1" wheel && \
    find /usr/local/lib/python3.11 -name "setuptools-70*" -exec rm -rf {} + 2>/dev/null || true && \
    find /usr/local/lib/python3.11 -name "msgpack-1.1*" -exec rm -rf {} + 2>/dev/null || true

# 2. Bağımlılıkları kopyala ve kur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Uygulama dosyalarını kopyala
COPY . .

# 4. Güvenlik: Non-root kullanıcı oluştur ve yetkilendir
RUN addgroup -S appgroup && adduser -S appuser -G appgroup && \
    chown -R appuser:appgroup /app

USER appuser

EXPOSE 5000

CMD ["python", "app.py"]