# استخدام نسخة بايثون خفيفة ومستقرة
FROM python:3.11-slim


ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    g++ \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
 
COPY main.py.

# Railway يستخدم متغير بيئة PORT بشكل ديناميكي
ENV PORT=8000
EXPOSE 8000

# أمر تشغيل السيرفر
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
