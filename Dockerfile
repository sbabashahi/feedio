FROM python:3.8-buster

MAINTAINER Saeed
LABEL name="Feedio server"

RUN mkdir /usr/src/app/

WORKDIR /usr/src/app/
COPY . .

RUN pip install -r requirements.txt
RUN ["chmod", "+x", "/usr/src/app/docker-entrypoint.sh"]

EXPOSE 8000

CMD ["gunicorn", "feedio.wsgi", "0:8000"]
