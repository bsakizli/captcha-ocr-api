FROM python:3.10-bullseye

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV FLAGS_use_mkldnn=0
ENV PIP_NO_CACHE_DIR=1

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# PaddleOCR opencv-python kuruyor, bu libGL ister.
# Onları kaldırıp sadece headless OpenCV bırakıyoruz.
RUN pip uninstall -y opencv-python opencv-contrib-python opencv-python-headless
RUN pip install opencv-python-headless==4.6.0.66

COPY . .

EXPOSE 8001

CMD ["gunicorn","--workers","1","--threads","4","--timeout","120","--bind","0.0.0.0:8001","api:app"]