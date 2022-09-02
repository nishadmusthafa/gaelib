# syntax=docker/dockerfile:1

FROM python:3.10.6-alpine3.16
RUN apk add git build-base linux-headers
# RUN curl –proto ‘=https’ –tlsv1.2 -sSf https://sh.rustup.rs | sh
WORKDIR /gaelib
COPY setup.py setup.py
RUN pip3 install --upgrade pip
RUN python3 -m pip install --upgrade setuptools
COPY test_requirements.txt test_requirements.txt
RUN python setup.py install
RUN pip3 install -r test_requirements.txt


