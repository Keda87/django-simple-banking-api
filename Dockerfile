FROM python:3.6-alpine
ENV PYTHONUNBUFFERED 1

RUN mkdir /sourcecode
WORKDIR /sourcecode
COPY src /sourcecode/
COPY requirements.txt /sourcecode/

RUN apk add\
    abuild\
    binutils\
    binutils-doc\
    build-base\
    gcc\
    gcc-doc\
    postgresql-dev\
    && rm -rf /var/cache/apk/*
RUN pip install -U pip && pip install --no-cache-dir -r requirements.txt

CMD gunicorn simplebanking.wsgi -b 0.0.0.0:5000 --log-level=debug --log-file=-