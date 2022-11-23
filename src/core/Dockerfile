FROM python:3.10

RUN pip install pip --upgrade
RUN pip install setuptools --upgrade

WORKDIR /build
COPY . core/

RUN pip install -e core