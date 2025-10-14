FROM python:3.10-slim

ENV TZ=Europe/Kyiv

# Встановлюємо необхідні пакети
RUN apt-get update && apt-get install --no-install-recommends -y \
    cron \
    htop \
    nano \
    curl \
    ffmpeg \
    python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Встановлюємо yt-dlp через pip (рекомендований спосіб)
RUN pip install --no-cache-dir yt-dlp

WORKDIR /FelArgailo

COPY . /FelArgailo

RUN pip install -r requirements.txt

CMD ["python3", "run.py"]