import time
from datetime import datetime

from django.conf import settings
from django.utils.translation import ugettext
from rest_framework.response import Response


class BaseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.DEBUG:
            st = datetime.now()
            response = self.get_response(request)
            print('Response Ready in: ', datetime.now() - st)
        else:
            response = self.get_response(request)
        return response

    def process_template_response(self, request, response):
        if not isinstance(response, Response):  # responses that are not for rest api
            return response
        message = None
        show_type = None
        if response.status_code == 403:
            # 403 Forbidden
            message = ugettext('Permission denied.')
            show_type = settings.MESSAGE_SHOW_TYPE['TOAST']

        elif response.status_code == 401:
            # 401 Unauthorized
            message = ugettext('Unauthorized access.')
            show_type = settings.MESSAGE_SHOW_TYPE['TOAST']

        elif response.status_code == 405:
            # 405 Method Not Allowed
            message = ugettext('Method not allowed.')

        elif response.status_code == 406:
            # 406 Not Acceptable
            message = ugettext('Not Acceptable.')

        elif response.status_code == 415:
            # 415 Unsupported media type
            message = ugettext('Unsupported media type.')
        elif response.status_code == 400:
            # 400 Bad Request
            message = ugettext('Bad Request.')

        elif response.status_code == 429:
            # 429 Too Many Requests
            message = ugettext('Too Many Requests.')
        if message:
            response.data = {
                'message': message,
                'errors': response.data['detail'],
                'success': False,
                'code': response.status_code,
                'current_time': round(time.time()),
                'show_type': show_type if show_type else settings.MESSAGE_SHOW_TYPE['NONE']
            }
        return response
