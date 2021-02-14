#!/bin/bash
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py collectstatic --clear --noinput
python3 manage.py collectstatic --noinput

touch /srv/logs/gunicorn.log
touch /srv/logs/access.log
tail -n 0 -f /srv/logs/*.log &

export SECRET_KEY=supersecretkey

echo Starting gunicorn.
exec gunicorn feedio.wsgi:application \
    --name feedio \
    --bind :8000 \
    --workers 3 \
    --log-level=info \
    --log-file=/srv/logs/gunicorn.log \
    --access-logfile=/srv/logs/access.log