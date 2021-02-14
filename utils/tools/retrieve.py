from rest_framework import generics

from utils import responses
from authnz.models import User


class RetrieveView(generics.RetrieveAPIView):

    def get(self, request, id=None, *args, **kwargs):
        try:
            if id is None and self.model == User:
                instance = request.user
            elif hasattr(self.model, 'is_deleted'):
                instance = self.model.objects.get(id=id, is_deleted=False)
            else:
                instance = self.model.objects.get(id=id)
            serialize_data = self.get_serializer(instance)
            return responses.SuccessResponse(serialize_data.data).send()
        except self.model.DoesNotExist as e:
            return responses.ErrorResponse(message='Instance does not Found.', status=404).send()
