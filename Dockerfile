FROM python:3.11

WORKDIR /FelArgailo

COPY . /FelArgailo

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

ENTRYPOINT ["python3"]
CMD ["run.py"]