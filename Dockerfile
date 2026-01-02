FROM python:3.13-slim AS base

RUN apt-get update
RUN apt-get install -y --no-install-recommends build-essential gcc

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements/prod.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --upgrade -r prod.txt

WORKDIR /app

RUN rm -rf /var/lib/apt/lists/*

# To be overriden if necessary
ENV CONFIG=./config/local.yaml

EXPOSE 8080

FROM base as prod

COPY bot bot
COPY config config

FROM prod AS dev

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
COPY requirements/*.txt ./
RUN pip install \
    -r tools.txt
