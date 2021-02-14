import requests  # pulling data
from bs4 import BeautifulSoup  # xml parsing
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
    except Exception as e:
        print('The scraping job failed. See exception:')
        print(e)
        return []


# print('Starting scraping')
# # hackernews_rss('https://www.varzesh3.com/rss/all')
# # hackernews_rss('https://www.isna.ir/rss')
# # hackernews_rss('https://digiato.com/feed/')
# hackernews_rss('https://www.zoomit.ir/feed/')
# print('Finished scraping')
