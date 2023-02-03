FROM python:3.9-slim
ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get -y install gcc
COPY ./requirements.in /requirements.in
RUN pip install -r /requirements.in
RUN mkdir -p /app
COPY . /app
WORKDIR /app