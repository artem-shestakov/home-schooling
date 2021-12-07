FROM python:3.9.5-alpine
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app
COPY entrypoint.sh /app

RUN pip install -r requirements.txt

COPY . /app
