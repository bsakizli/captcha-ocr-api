FROM python:3.10-bullseye

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV FLAGS_use_mkldnn=0
ENV PIP_NO_CACHE_DIR=1

RUN sed -i 's|http://deb.debian.org|https://deb.debian.org|g' /etc/apt/sources.list && \
    sed -i 's|http://security.debian.org|https://security.debian.org|g' /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN pip uninstall -y opencv-python opencv-contrib-python opencv-python-headless
RUN pip install opencv-python-headless==4.6.0.66

COPY . .

EXPOSE 8001

CMD ["gunicorn","--workers","1","--threads","4","--timeout","180","--bind","0.0.0.0:8001","api:app"]