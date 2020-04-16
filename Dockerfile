FROM python:3.7-alpine

RUN python -m pip install --upgrade pip

RUN mkdir /simpleshortener
WORKDIR /simpleshortener

COPY simpleshortener ./

RUN pip install -r ./requirements.txt

COPY simpleshortener ./

EXPOSE 7878

ENTRYPOINT gunicorn -b 0.0.0.0:7878 "wsgi:gunicorn_entry()"
