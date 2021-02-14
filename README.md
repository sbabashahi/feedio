This is a test Project with python3.8, Django, DRF, Postgresql, Redis, Celery and Celery Beat.

The idea is to create a simple RSS scraper which saves RSS feeds to a database and lets a user view and manage his 
feeds via a simple API.

We have a swagger endpoint.


# Create DB
    
    CREATE USER feedio WITH PASSWORD 'feediopass';
    ALTER USER feedio WITH SUPERUSER;
    CREATE DATABASE feediodb;


# RSS Feed example

    https://www.varzesh3.com/rss/all
    https://www.isna.ir/rss
    https://digiato.com/feed/
    https://www.zoomit.ir/feed/
    
# tests

    ./manage.py test
    
    We have some integration test.


