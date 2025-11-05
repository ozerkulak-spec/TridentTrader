FROM python:3.11-slim

WORKDIR /app

# Sistem bağımlılıkları
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python bağımlılıkları
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyaları
COPY bot_v2_pro.py .
COPY templates ./templates

# Database dizini
RUN mkdir -p /app/data

# Port
EXPOSE 8000

# Başlat
CMD ["uvicorn", "bot_v2_pro:app", "--host", "0.0.0.0", "--port", "8000"]
