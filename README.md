This is a test Project with python3.8, Django, DRF, Postgresql, Redis, Celery and Celery Beat.

The idea is to create a simple RSS scraper which saves RSS feeds to a database and lets a user view and manage his 
feeds via a simple API.

### Run it with docker

    docker-compose up

### We have a swagger endpoint:

    http://localhost:8008/swagger/

### For first use and creating initial data you can use:
    
    http://localhost:8008/utils_views/data_test/
 
### Create DB If you want to use it without docker
    
    CREATE USER feedio WITH PASSWORD 'feediopass';
    ALTER USER feedio WITH SUPERUSER;
    CREATE DATABASE feediodb;


### RSS Feed example

    https://www.varzesh3.com/rss/all
    https://www.isna.ir/rss
    https://digiato.com/feed/
    https://www.zoomit.ir/feed/
    
### Tests

     We have some integration test.

    ./manage.py test


### Authorization

    JWT token used for authorization you can get it from /authnz/login_email/ with email & pass
    also refresh your token from /authnz/refresh_my_token/
    
    Add it to your request header like Authorization: JWT your-jwt-token


### Async Tasks

    We have 2 tasks using celery and celery beat.
    
    check_new_rss -> as soosn as new Rss create by API /rss/rss/ it would run in background to get feeds from that Rss
    
    check_rss_every_hour -> every hour it would be run with use of celery beat and try to get lastest feeds
     from all active Rss 
     
    ![Alt text](https://github.com/sbabashahi/feedio/blob/master/hourly_task.png?raw=true)
