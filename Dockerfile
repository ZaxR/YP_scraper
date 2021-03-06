# base image
FROM python:3.6.8-alpine

# Correct celery stdout log anomalies; see https://www.distributedpython.com/2018/11/15/celery-docker/
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8 PYTHONUNBUFFERED=1

# set working directory
WORKDIR /usr/src/app

# Required for Gevent and lxml
RUN apk add --no-cache python3 \
					   python3-dev \
					   g++ \
					   gcc \
					   musl-dev \
					   zlib-dev \
					   libffi-dev \
					   libxslt-dev \
					   openssl-dev \
					   ca-certificates \
					   bash \
					   postgresql \
					   postgresql-dev

# add requirements
COPY ./requirements.txt /usr/src/app/requirements.txt

# install requirements
RUN pip install -r requirements.txt

# add app
COPY . /usr/src/app
