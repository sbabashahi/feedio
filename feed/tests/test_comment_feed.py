import requests
from django.test import TestCase
from unittest.mock import Mock, patch

from authnz.models import User
from feed.models import Feed, Rss
from utils.tasks import check_rss_every_hour


mock = Mock()


class RssTestCase(TestCase):
    header = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        data = {
            'email': 'saeed@test.com',
            'password': '123456'
        }
        user = User.register_user(email=data['email'], password=data['password'])
        user.confirm_email()
        user.is_staff = True
        user.is_superuser = True
        user.save()

        cls.header = {'HTTP_AUTHORIZATION': f'JWT {user.generate_token()}'}

        varzesh3_data = {
            'title': 'Varzesh3',
            'link': 'https://www.varzesh3.com/rss/all'
        }
        rss = Rss(**varzesh3_data)
        rss.save()

        feed_data = {
            'title': 'some title',
            'link': 'some link',
            'published': 1613298529,
            'description': 'some description',
            'rss': rss,
        }
        feed = Feed(**feed_data)
        feed.save()

    def test_feed(self):
        self.assertEqual(Feed.objects.count(), 1, 'Wrong feed count.')

        resp = self.client.get('/feed/feed_list/', **self.header)
        self.assertEqual(resp.status_code, 200, 'Wrong status code.')
        data = resp.json()

        self.assertEqual(data['total'], 1, 'Wrong total feed.')
        self.assertEqual(data['data'][0]['title'], Feed.objects.first().title, 'Wrong feed title.')
        self.assertEqual(data['data'][0]['rss']['title'], Rss.objects.first().title, 'Wrong feed title.')

        resp = self.client.post('/feed/favorite_feed/{}/'.format(data['data'][0]['id']), **self.header)
        self.assertEqual(resp.status_code, 201, 'Wrong status type.')

        resp = self.client.get('/feed/favorite_feed/', **self.header)
        data = resp.json()
        self.assertEqual(data['total'], 1, 'Wrong total feed.')
        self.assertEqual(data['data'][0]['id'], Feed.objects.first().id, 'Wrong feed id.')

        resp = self.client.delete('/feed/favorite_feed/{}/'.format(data['data'][0]['id']), **self.header)
        self.assertEqual(resp.status_code, 204, 'Wrong status type.')

        resp = self.client.get('/feed/favorite_feed/', **self.header)
        data = resp.json()
        self.assertEqual(data['total'], 0, 'Wrong total feed.')

    def test_comment(self):
        data = {
            'body': 'Body of comment',
            'feed': {
                'id': Feed.objects.first().id,
            },
        }
        resp = self.client.post('/comment/comment/', data=data, content_type='application/json', **self.header)
        self.assertEqual(resp.status_code, 201, 'Wrong status type.')
        self.assertEqual(resp.json()['data']['body'], data['body'], 'Wrong comment body.')

        resp = self.client.get('/feed/comment_list/{}/'.format(data['feed']['id']), **self.header)
        self.assertEqual(resp.status_code, 200, 'Wrong status type.')
        data = resp.json()
        self.assertEqual(data['total'], 1, 'Wrong total coomment.')
