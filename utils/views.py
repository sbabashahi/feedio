from rest_framework import decorators, exceptions, generics, serializers

from authnz.models import User
from feed.models import Rss
from utils import responses, exceptions as authnz_exceptions, tasks


@decorators.authentication_classes([])
@decorators.permission_classes([])
class CreateDataTestView(generics.CreateAPIView):
    """
    post:

        Create data test

        admin user

            admin@admin.com     feedio2021

        and Rss

            https://www.varzesh3.com/rss/all

            https://www.isna.ir/rss

    """
    serializer_class = serializers.Serializer

    def post(self, request):
        try:
            admin_data = {
                'email':    'admin@admin.com',
                'password': 'feedio2021',
            }
            user = User.register_user(admin_data['email'], admin_data['password'])
            user.is_staff = True
            user.is_superuser = True
            user.confirm_email()

            varzesh3_data = {
                'title': 'Varzesh3',
                'link': 'https://www.varzesh3.com/rss/all',
            }

            isna_data = {
                'title': 'Isna',
                'link': 'https://www.isna.ir/rss',
            }

            varzesh3_rss = Rss(**varzesh3_data)
            varzesh3_rss.save()
            tasks.check_new_rss.apply_async(args=(varzesh3_rss.id,), retry=False)
            isna_rss = Rss(**isna_data)
            isna_rss.save()
            tasks.check_new_rss.apply_async(args=(isna_rss.id,), retry=False)

            return responses.SuccessResponse({}, status=201).send()
        except (authnz_exceptions.CustomException, exceptions.ValidationError) as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()
