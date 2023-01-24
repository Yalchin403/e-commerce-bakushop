FROM python:3.9-slim
ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get -y install gcc
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
RUN mkdir -p /app
COPY . /app
WORKDIR /app