FROM python:3.10

RUN apt-get update
RUN apt-get install -y libhdf5-dev liblapack-dev gfortran cmake build-essential python3-dev automake autoconf
RUN apt install -y libatlas-base-dev python3-dev gfortran pkg-config libfreetype6-dev hdf5-tools
RUN ln -s /usr/include/locale.h /usr/include/xlocale.h

RUN curl -L -o ta-lib-0.4.0-src.tar.gz  http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz 
RUN tar xvfz ta-lib-0.4.0-src.tar.gz
WORKDIR /ta-lib
RUN cp /usr/share/automake-1.16/config.guess .
RUN ./configure --prefix=/usr/local
RUN make
RUN make install
RUN apt upgrade -y 

WORKDIR /build
COPY src .

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install --upgrade cython

RUN pip install -e zipline
RUN pip install -e core

WORKDIR /build/zipline
CMD ["python", "-m", "app"]
