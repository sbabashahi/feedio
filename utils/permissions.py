from django.utils.translation import ugettext
from django.core.cache import cache
from django.conf import settings
from rest_framework import permissions

from utils.exceptions import CustomException


class SuperUserPermission(permissions.BasePermission):
    """
    Global permission Super user
    """

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        return False


class StaffPermission(permissions.BasePermission):
    """
    Global permission check for Staff

    Is super user or has perm for this api

    perm will create from api /api/update_permissions_list/
    """

    def has_permission(self, request, view):
        if (request.user.is_staff and request.user.has_perm('auth.' + view.__class__.__name__))\
                or request.user.is_superuser:
            return True
        return False


def check_send_email_permission(email):
    email_count = cache.get('{}_{}'.format(settings.EMAIL_SEND_COUNT, email), 0)
    if email_count >= settings.MAX_EMAIL_SEND_COUNT:
        raise CustomException(detail=ugettext('Max email send reached, try later.'), code=403)


def count_send_email(email):
    email_count = cache.get('{}_{}'.format(settings.EMAIL_SEND_COUNT, email), 0)
    cache.set('{}_{}'.format(settings.EMAIL_SEND_COUNT, email), email_count+1, timeout=settings.MAX_EMAIL_SEND_TIMEOUT)
