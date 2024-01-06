FROM python:3.10-bullseye
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -y
COPY . /app
WORKDIR /app

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install -r requirements.txt