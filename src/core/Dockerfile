FROM python:3.10

RUN apt-get update 
RUN apt-get install cmake build-essential python-dev -y

RUN pip install pip --upgrade
RUN pip install setuptools --upgrade

WORKDIR /build
COPY . core/

RUN pip install -e core