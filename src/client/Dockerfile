FROM python:3.10

WORKDIR /build
COPY . client/

RUN pip install -e client

# Install git version of core, TODO: Better way to do this?
COPY ../core /tmp/core/

RUN pip install -e /tmp/core
