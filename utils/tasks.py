from celery import shared_task  # , Celery
from feedio.celery import app
from requests.exceptions import RequestException

from feed.models import Rss, Feed
from scrapper.scraping import scrap_rss

# app = Celery()  # TODO


@app.task(autoretry_for=(RequestException,), retry_kwargs={'max_retries': 3, 'countdown': 5}, retry_backoff=True)
def check_rss_every_hour():
    for rss in Rss.objects.filter(is_active=True):
        last_time = rss.feed_set.first()
        last_time = last_time.published if last_time else 0
        feed_list = scrap_rss(rss.link, last_time)
        for feed in feed_list:
            feed['rss'] = rss
            feed_item = Feed(**feed)
            feed_item.save()


@shared_task
def check_new_rss(rss_id):
    rss = Rss.objects.get(id=rss_id)
    feed_list = scrap_rss(rss.link, 0)
    for feed in feed_list:
        feed['rss'] = rss
        feed_item = Feed(**feed)
        feed_item.save()
