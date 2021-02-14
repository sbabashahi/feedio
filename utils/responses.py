"""
main response handler, some of response handel throw  middleware
"""
import time
import json

from django.http import HttpResponse
from django.conf import settings


class BaseResponse:
    def send(self):
        status = self.__dict__.pop('status')
        return HttpResponse(
            json.dumps(self.__dict__),
            status=status,
            content_type="application/json"
        )


class ErrorResponse(BaseResponse):
    def __init__(self, message, dev_error=None,show_type=settings.MESSAGE_SHOW_TYPE['TOAST'], status=400):
        self.message = message
        self.dev_error = dev_error
        self.show_type = show_type
        self.current_time = round(time.time())
        self.success = False
        self.status = status


class SuccessResponse(BaseResponse):
    def __init__(self, data=None, message=None, show_type=settings.MESSAGE_SHOW_TYPE['TOAST'], status=200, **kwargs):
        self.data = data
        self.message = message
        self.show_type = show_type
        self.current_time = round(time.time())
        self.success = True
        self.index = kwargs['index'] if kwargs.get('index') is not None else None
        self.total = kwargs['total'] if kwargs.get('total') is not None else None
        self.status = status


def handler404(request, exception):
    message = 'Not found'
    dev_error = 'Not found path {}'.format(request.path)
    show_type = settings.MESSAGE_SHOW_TYPE['NONE']
    return ErrorResponse(message=message, dev_error=dev_error, show_type=show_type, status=404).send()


def handler500(request):
    message = 'Server error'
    show_type = settings.MESSAGE_SHOW_TYPE['NONE']
    return ErrorResponse(message=message, show_type=show_type, status=500).send()
