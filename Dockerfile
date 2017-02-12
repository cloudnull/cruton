FROM python:3.5.3-alpine
MAINTAINER Victor Palma <devx@desmind.org>

ENV LANG en_US.UTF-8

COPY ./requirements.txt /usr/local/src/cruton/requirements.txt

RUN apk -U upgrade && \
    apk -U add ca-certificates build-base linux-headers && \
    cd /usr/local/src && \
    pip3 install --no-cache-dir --compile -U -r cruton/requirements.txt && \
    apk -U del build-base linux-headers && \
    apk -U add git && \
    adduser -h / -H -D cruton && \
    rm /var/cache/apk/*

COPY . /usr/local/src/cruton

RUN apk -U add git && \
    rm /var/cache/apk/* && \
    pip3 install --no-cache-dir --compile file:///usr/local/src/cruton#egg=cruton

VOLUME /etc/cruton/
EXPOSE 5150
CMD []
