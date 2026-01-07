FROM python:3.11.7-slim

ENV TZ=Europe/Kyiv

RUN apt-get update && apt-get install --no-install-recommends -y \
    cron \
    curl \
    unzip \
    ffmpeg \
    python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir yt-dlp

RUN curl -fsSL https://deno.land/install.sh | sh
# Set environment variables to add Deno to the PATH
ENV DENO_INSTALL="/root/.deno"
ENV PATH="$DENO_INSTALL/bin:$PATH"

WORKDIR /FelArgailo

COPY . /FelArgailo

RUN pip install -r requirements.txt

CMD ["python3", "run.py"]