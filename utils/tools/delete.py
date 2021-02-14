from django.utils.translation import ugettext
from rest_framework import generics

from utils import exceptions, responses, permissions


class DeleteView(generics.DestroyAPIView):
    """
    Delete instance
    """
    def delete(self, request, id):
        try:
            if hasattr(self.model, 'is_deleted'):
                instance = self.model.objects.get(id=id, is_deleted=False)
            else:
                instance = self.model.objects.get(id=id)
            permissions.check_delete_permission(request, instance)
            if hasattr(self.model, 'is_deleted'):
                instance.is_deleted = True
                instance.save()
            else:
                instance.delete()
            data = {}
            return responses.SuccessResponse(data, status=204).send()
        except (self.model.DoesNotExist, exceptions.CustomException) as e:
            return responses.ErrorResponse(message=ugettext('Instance does not exist.'), status=404).send()
