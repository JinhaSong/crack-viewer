FROM ubuntu:16.04

RUN apt-get update \
    && apt-get -y install python \
    python-pip \
    python-dev \
    git \
    libglib2.0-0 libsm6 libxrender1

RUN pip install --upgrade pip
RUN pip install setuptools

WORKDIR /workspace
ADD . .

RUN chmod -R a+w /workspace

EXPOSE 8000
