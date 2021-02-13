import time
import uuid

from django.utils.translation import ugettext
from querystring_parser import parser

from utils import exceptions


def now_time():
    return round(time.time())


def uuid_str():
    return ''.join(str(uuid.uuid4()).split('-'))


def jwt_get_secret_key(user):
    """
    Use this in generating and checking JWT token,
    and when logout jwt_secret will change so previous JWT token wil be invalidate
    :param user:
    :return:
    """
    return user.jwt_secret


def jwt_response_payload_handler(token, user):
    """
    Returns the response data for both the login and refresh views.
    Override to return a custom response such as including the
    serialized representation of the User.

    """
    data = {
        'token': token,
        'user': {
            'is_provider': user.is_provider,
        }
    }
    return data


def pagination_util(request):
    arguments = parser.parse(request.GET.urlencode())
    try:
        size = int(arguments.pop('size', 20))
        index = int(arguments.pop('index', 0))
    except ValueError:
        raise exceptions.CustomException(detail=ugettext('Size and index query param for pagination must be integer.'))
    size = index + size
    return index, size, args
