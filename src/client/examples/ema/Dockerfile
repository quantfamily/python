FROM python:3.9

RUN apt-get update 
RUN apt-get install cmake build-essential python-dev -y

RUN pip install pip --upgrade
RUN pip install foreverbull --upgrade

RUN curl -L -o ta-lib-0.4.0-src.tar.gz  http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz 
RUN tar xvfz ta-lib-0.4.0-src.tar.gz
WORKDIR /ta-lib
RUN ls
RUN cp /usr/share/automake-1.16/config.guess .
RUN ./configure --prefix=/usr/local
RUN make
RUN make install
RUN apt upgrade -y 

RUN pip install ta-lib

WORKDIR /app
WORKDIR /app/foreverbull
COPY . /app/foreverbull/

RUN pip install -e .
RUN pip install ta-lib

COPY examples/ema/ema.py /app/foreverbull/examples/ema.py

ENV PYTHONPATH="${PYTHONPATH}:/app"

ENTRYPOINT [ "foreverbull", "run", "examples/ema.py" ]