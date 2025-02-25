FROM python:3.10-slim

WORKDIR /keitaro-clicks-viewer

COPY . /keitaro-clicks-viewer

RUN python -m pip install -r requirements.txt

CMD ["python3", "run.py"]
