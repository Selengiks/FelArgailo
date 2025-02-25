FROM python:3.10-slim

ENV TZ=Europe/Kyiv

# Встановлюємо необхідні пакети
RUN apt-get update && apt-get install --no-install-recommends -y cron htop nano curl

WORKDIR /keitaro-clicks-viewer

COPY . /keitaro-clicks-viewer

RUN pip install -r requirements.txt

CMD ["python3", "run.py"]
