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


def check_send_email_permission(email):
    email_count = cache.get('{}_{}'.format(settings.EMAIL_SEND_COUNT, email), 0)
    if email_count >= settings.MAX_EMAIL_SEND_COUNT:
        raise CustomException(detail=ugettext('Max email send reached, try later.'), code=403)


def count_send_email(email):
    email_count = cache.get('{}_{}'.format(settings.EMAIL_SEND_COUNT, email), 0)
    cache.set('{}_{}'.format(settings.EMAIL_SEND_COUNT, email), email_count+1, timeout=settings.MAX_EMAIL_SEND_TIMEOUT)


def check_perm_owner_update(request, instance):
    if hasattr(instance, 'user') and instance.user == request.user:
        return True
    elif hasattr(instance, 'user'):
        raise CustomException(detail=_('No Permission to update'), code=403)
    elif request.user.is_superuser:
        return True
    else:
        raise CustomException(detail=_('No Permission to update'), code=403)


def check_delete_permission(request, instance):
    if request.user.is_superuser:
        return True
    elif hasattr(instance, 'user') and instance.user == request.user:
        return True
    else:
        raise CustomException(detail=_('No Permission to delete'), code=403)
