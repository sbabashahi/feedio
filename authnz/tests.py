from django.test import TestCase

from authnz.models import User


class AnimalTestCase(TestCase):

    def test_user_model_methods(self):
        """
        Test User methods
        :return:
        """
        email = 'test@email.com'
        password = '123456'
        user = User.register_user(email, password)
        self.assertEqual(user.username, email, 'Wrong username')
        self.assertEqual(user.email, email, 'Wrong email')
        self.assertEqual(user.check_password(password), True, 'Wrong password')

        new_password = '654321'
        user.update_password(new_password)
        self.assertEqual(user.check_password(password), False, 'Wrong password')
        self.assertEqual(user.check_password(new_password), True, 'Wrong password')

        self.assertEqual(user.email_confirmed, False, 'Wrong email confirmed')
        user.confirm_email()
        self.assertEqual(user.email_confirmed, True, 'Wrong email confirmed')

