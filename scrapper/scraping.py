import requests
from bs4 import BeautifulSoup
from celery.utils.log import get_task_logger
from dateutil.parser import parse


def scrap_rss(url: str, last_time)->dict:
    article_list = []
    try:
        resp = requests.get(url)
        soup = BeautifulSoup(resp.content, features='xml')

        articles = soup.findAll('item')
        for a in articles:
            title = a.find('title').text
            link = a.find('link').text
            published = parse(a.find('pubDate').text).timestamp()
            description = a.find('description').text
            if published <= last_time:
                break
            article = {
                'title': title,
                'link': link,
                'published': published,
                'description': description
            }

            article_list.append(article)
        return article_list
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException
    except Exception as e:
        logger = get_task_logger(__name__)
        logger.error(str(e))
        return []
