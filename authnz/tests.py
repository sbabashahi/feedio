import re

from django.core import mail
from django.test import TestCase

from authnz.models import User


class UserTestCase(TestCase):

    def test_user_model_methods(self):
        """
        Test User model methods
        :return:
        """
        # test user register
        email = 'test@email.com'
        password = '123456'
        user = User.register_user(email, password)
        self.assertEqual(user.username, email, 'Wrong username')
        self.assertEqual(user.email, email, 'Wrong email')
        self.assertEqual(user.check_password(password), True, 'Wrong password')
        # test user update password
        new_password = '654321'
        user.update_password(new_password)
        self.assertEqual(user.check_password(password), False, 'Wrong password')
        self.assertEqual(user.check_password(new_password), True, 'Wrong password')
        # test email confirm
        self.assertEqual(user.email_confirmed, False, 'Wrong email confirmed')
        user.confirm_email()
        self.assertEqual(user.email_confirmed, True, 'Wrong email confirmed')

    def test_user_register_login_refresh_token(self):
        """
        Test authnz APIs
        :return:
        """
        # test register API
        data = {
            'email': 'saeed@test.com',
            'password': '123456'
        }
        resp = self.client.post('/authnz/register_email/', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, 201, 'Wrong status code')
        self.assertEqual(len(mail.outbox), 1, 'Email sending problem')
        self.assertEqual(mail.outbox[0].to, [data['email']], 'Email sending problem')
        self.assertEqual(mail.outbox[0].subject, 'Confirm your email', 'Wrong email subject')

        # test email approve API
        link = re.findall(
            'http://testserver/authnz/approve_email/[0-9A-Za-z_\-\']+/[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,32}/',
            mail.outbox[0].alternatives[0][0]
        )
        self.assertEqual(len([link]), 1, 'Wrong email confirmation link')

        resp = self.client.get(link[0])
        self.assertEqual(resp.status_code, 200, 'Wrong status code')

        resp = self.client.get(link[0])
        self.assertEqual(resp.status_code, 400, 'Wrong status code')
        # test login API
        resp = self.client.post('/authnz/login_email/', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, 200, 'Wrong status code')
        self.assertIsInstance(resp.json(), dict, 'Wrong response type')
        # test refresh token API
        headers = {'HTTP_AUTHORIZATION': f'JWT {resp.json()["data"]["token"]}'}
        resp = self.client.get('/authnz/refresh_my_token/', **headers)
        self.assertEqual(resp.status_code, 200, 'Wrong status code')
        self.assertIsInstance(resp.json(), dict, 'Wrong response type')
