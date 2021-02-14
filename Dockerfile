FROM python:3.8-alpine

MAINTAINER Saeed
LABEL name="Ubuntu Python3 server"

RUN mkdir /usr/src/app/

WORKDIR /usr/src/app/
COPY . .

RUN pip install -r requirements.txt
RUN ["chmod", "+x", "/docker-entrypoint.sh"]

EXPOSE 8000

CMD ["gunicorn", "feedio.wsgi", "0:8000"]
