FROM python:3.10-slim

ENV TZ=Europe/Kyiv

RUN apt-get update && apt-get install --no-install-recommends -y \
    cron htop nano curl && rm -rf /var/lib/apt/lists/* \

WORKDIR /keitaro-clicks-viewer

COPY . /keitaro-clicks-viewer

RUN pip install -r requirements.txt

CMD ["python3", "run.py"]
