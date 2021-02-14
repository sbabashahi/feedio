from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.db import models
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils import timezone
from django.utils.translation import ugettext
from rest_framework_jwt.utils import jwt_payload_handler, jwt_encode_handler

from utils import permissions, utils


class SetEmailActivationTokenGenerator(PasswordResetTokenGenerator):
    """
    Set email verification code
    """
    def _make_hash_value(self, user, timestamp):
        return (
                str(user.pk) + str(timestamp) +
                str(user.email_confirmed)
        )


email_activation_token = SetEmailActivationTokenGenerator()


class User(AbstractUser):
    jwt_secret = models.CharField(max_length=32, default=utils.uuid_str,
                                  help_text=ugettext('Private key of user JWT Token.'))
    email_confirmed = models.BooleanField(default=False, help_text=ugettext('Email verified.'))

    def __str__(self):
        return self.username

    def renew_jwt(self):
        self.jwt_secret = utils.uuid_str()
        self.save()

    def send_email_confirm(self, request):
        current_site = get_current_site(request)
        subject = 'Confirm your email'
        message = render_to_string('authnz/email_verification.html', {
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(self.pk)),
            'token': email_activation_token.make_token(self),
            'http_type': 'https' if request.is_secure() else 'http',
        })

        resp = send_mail(subject=subject, message='', from_email=settings.EMAILS_LIST.get("support"),
                         recipient_list=[self.email], html_message=message)
        permissions.count_send_email(self.email)

    def save_last_login(self):
        self.last_login = timezone.now()
        self.save()

    def confirm_email(self):
        self.email_confirmed = True
        self.save()

    def update_password(self, raw_password):
        self.set_password(raw_password)
        self.save()

    @classmethod
    def register_user(cls, email, password):
        user = cls(username=email, email=email)
        user.set_password(password)
        user.save()
        return user

    def generate_token(self):
        payload = jwt_payload_handler(self)
        return jwt_encode_handler(payload)
