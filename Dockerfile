FROM ubuntu:16.04

RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10
RUN apt-get update && apt-get install -y \
    python \
    python-dev \
    python3.5 \
    python3.5-dev \
    python-pip \
    libssl-dev \
    libpq-dev \
    #git \
    #build-essential \
    libfontconfig1 \
    libfontconfig1-dev \
    wget \
    autoconf \
    automake \
    libtool \
    #curl \
    g++ \
    unzip


RUN pip install setuptools pip --upgrade --force-reinstall

COPY . /opt
RUN pip install -r requirements.txt

WORKDIR /opt
RUN wget https://github.com/google/protobuf/releases/download/v3.6.1/protoc-3.6.1-linux-x86_64.zip
# Unzip
RUN unzip protoc-3.6.1-linux-x86_64.zip -d protoc3

# Move protoc to /usr/local/bin/
RUN mv protoc3/bin/* /usr/local/bin/

# Move protoc3/include to /usr/local/include/
RUN mv protoc3/include/* /usr/local/include/
RUN ldconfig

RUN wget https://github.com/protocolbuffers/protobuf/releases/download/v3.6.1/protobuf-python-3.6.1.zip
RUN unzip protobuf-python-3.6.1.zip -d protoc-python
WORKDIR /opt/protoc-python/protobuf-3.6.1/python
RUN python setup.py build
RUN python setup.py test
WORKDIR /opt
RUN wget https://developers.google.com/transit/gtfs-realtime/gtfs-realtime.proto
RUN protoc --python_out=. ./gtfs-realtime.proto

ENTRYPOINT ["python",  "/opt/entrypoint.py"]