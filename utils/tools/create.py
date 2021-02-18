from django.db.utils import IntegrityError
from django.utils.translation import ugettext
from rest_framework import generics
from rest_framework.exceptions import ValidationError

from utils.exceptions import CustomException
from utils import responses


class CreateView(generics.CreateAPIView):

    def post(self, request, *args, **kwargs):
        try:
            serialize_data = self.get_serializer(data=request.data)
            if serialize_data.is_valid(raise_exception=True):
                self.perform_create(serialize_data)
                return responses.SuccessResponse(serialize_data.data, status=201).send()
        except IntegrityError as e:
            return responses.ErrorResponse(message=ugettext('DB Integrity Error in creation.'),
                                           dev_error=str(e), status=409).send()
        except (CustomException, ValidationError) as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()
