FROM python:3.10

RUN apt update
RUN apt install -y cmake build-essential python-dev

RUN pip install pip --upgrade
RUN pip install setuptools --upgrade

WORKDIR /build
COPY src .

RUN pip install -e core