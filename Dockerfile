FROM python:3.11-alpine

LABEL maintainer="DevSecOps Engineering"
LABEL description="Hardened Flask Application for Security Pipeline"

WORKDIR /app

# 1. Pip, setuptools ve msgpack'i küresel olarak en güncel sürümlere yükselt
RUN pip install --no-cache-dir --upgrade pip "setuptools>=78.1.1" "msgpack>=1.2.1" wheel

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