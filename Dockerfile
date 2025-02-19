FROM python:3.11

WORKDIR /keitaro-clicks-viewer

COPY . /keitaro-clicks-viewer

RUN python -m pip install -r requirements.txt

CMD ["python3", "run.py"]
