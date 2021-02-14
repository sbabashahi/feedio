from rest_framework import generics
from rest_framework.exceptions import ValidationError

from authnz.models import User
from utils import exceptions, responses, permissions


class UpdateView(generics.UpdateAPIView):

    def put(self, request, id=None):
        try:
            if id:
                instance = self.model.objects.get(id=id)
                permissions.check_perm_owner_update(request, instance)
            elif self.model == User:
                instance = request.user

            serialized_data = self.get_serializer(instance, data=request.data)
            if serialized_data.is_valid(raise_exception=True):
                self.perform_update(serialized_data)
                return responses.SuccessResponse(serialized_data.data).send()
        except (exceptions.CustomException, ValidationError, self.model.DoesNotExist) as e:
                return responses.ErrorResponse(message=e.detail, status=e.status_code).send()

    def patch(self, request, id=None):  # just send parameters you want to update, don't need all of them
        try:
            if id:
                instance = self.model.objects.get(id=id)
                permissions.check_perm_owner_update(request, instance)
            elif self.model == User:
                instance = request.user

            serialized_data = self.get_serializer(instance, data=request.data, partial=True)
            if serialized_data.is_valid(raise_exception=True):
                self.perform_update(serialized_data)
                return responses.SuccessResponse(serialized_data.data).send()
        except (exceptions.CustomException, ValidationError, self.model.DoesNotExist) as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()
