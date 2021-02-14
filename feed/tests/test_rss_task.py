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

    def test_create_rss(self):
        with patch('utils.tasks.check_new_rss'):
            data = {
                'title': 'Varzesh3',
                'link': 'https://www.varzesh3.com/rss/all'
            }
            resp = self.client.post('/rss/rss/', data=data, content_type='application/json', **self.header)
            self.assertEqual(resp.status_code, 201, 'Wrong status type')
            self.assertEqual(Rss.objects.count(), 1, 'Wrong number of rss')
            data = {
                'title': 'Zoomit',
                'link': 'https://www.zoomit.ir/feed/'
            }
            resp = self.client.post('/rss/rss/', data=data, content_type='application/json', **self.header)
            self.assertEqual(Rss.objects.count(), 2, 'Wrong number of rss')

    def test_task_rss(self):

        def scrap(link, time):
            data = {
                'https://www.varzesh3.com/rss/all': [
                    {
                        'title': 'some title',
                        'link': 'some link',
                        'published': 1613298529,
                        'description': 'some description',
                    }
                ],
            }
            return data.pop(link, [])

        data_varzesh = {
            'title': 'Varzesh3',
            'link': 'https://www.varzesh3.com/rss/all'
        }
        rss_varzesh = Rss(**data_varzesh)
        rss_varzesh.save()
        data_zoomit = {
            'title': 'Zoomit',
            'link': 'https://www.zoomit.ir/feed/'
        }
        rss_zoomit = Rss(**data_zoomit)
        rss_zoomit.save()
        with patch('utils.tasks.check_rss_every_hour.retry', side_effect=check_rss_every_hour):
            with patch('utils.tasks.check_rss_every_hour.retry', side_effect=check_rss_every_hour):
                with patch('utils.tasks.scrap_rss', side_effect=scrap):
                    check_rss_every_hour()
                    self.assertEqual(Feed.objects.count(), 1, 'Wrong number of feeds')

