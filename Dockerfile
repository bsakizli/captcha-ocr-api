FROM python:3.10-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV FLAGS_use_mkldnn=0
ENV PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    wget \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

COPY warmup.py .
RUN python warmup.py

COPY . .

EXPOSE 8001

CMD ["gunicorn", "--workers", "1", "--threads", "4", "--timeout", "120", "--bind", "0.0.0.0:8001", "api:app"]