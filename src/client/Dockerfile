FROM python:3.10

RUN apt update
RUN apt install -y cmake build-essential python-dev

RUN pip install pip --upgrade
RUN pip install setuptools --upgrade
RUN pip install flit


WORKDIR /build
COPY src .

ENV FLIT_ROOT_INSTALL 1
RUN cd client && flit install && cd ..
RUN cd core && flit install && cd ..

RUN echo "" >> ema.py

CMD [ "python", "-m", "foreverbull", "run", "ema.py" ]
