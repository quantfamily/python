FROM python:3.9

RUN apt update
RUN apt install -y cmake build-essential python-dev

RUN pip install pip --upgrade
RUN pip install setuptools --upgrade
RUN pip install flit

WORKDIR /build
COPY src .

ENV FLIT_ROOT_INSTALL 1
RUN cd core && flit install && cd ..
