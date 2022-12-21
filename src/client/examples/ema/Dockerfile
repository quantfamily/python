FROM spawn-client:latest

RUN apt-get update 
RUN apt-get install cmake build-essential python-dev -y

RUN pip install pip --upgrade

WORKDIR /build
RUN curl -L -o ta-lib-0.4.0-src.tar.gz  http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz 
RUN tar xvfz ta-lib-0.4.0-src.tar.gz
WORKDIR /build/ta-lib
RUN cp /usr/share/automake-1.16/config.guess .
RUN ./configure --prefix=/usr/local
RUN make
RUN make install
RUN apt upgrade -y 

RUN pip install ta-lib

WORKDIR /algos
COPY ema.py ema.py

RUN pip install ta-lib

CMD [ "python", "-m", "foreverbull", "run", "ema.py" ]
