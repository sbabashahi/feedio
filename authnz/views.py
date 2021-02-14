from django.shortcuts import render
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import ugettext
from rest_framework import decorators, exceptions, generics, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.utils import jwt_payload_handler, jwt_encode_handler

from authnz import serializers as authnz_serializers
from authnz.models import User, email_activation_token

from utils import responses, exceptions as authnz_exceptions, permissions, utils
from utils.tools import retrieve, update


@decorators.authentication_classes([])
@decorators.permission_classes([])
class UserRegisterEmailView(generics.CreateAPIView):
    """
    post:

        Main Register with email & password


            email min 5, max 50

            password min 5, max 50

    """
    serializer_class = authnz_serializers.RegisterLoginEmailSerializer

    def post(self, request):
        try:
            serialized_data = self.serializer_class(data=request.data)
            if serialized_data.is_valid(raise_exception=True):
                email = serialized_data.data['email']
                password = serialized_data.data['password']
                user_list = User.objects.filter(email=email, email_confirmed=True)
                if user_list:
                    raise authnz_exceptions.CustomException(detail=ugettext('You registered before.'))

                permissions.check_send_email_permission(email)

                try:  # check for previous used email
                    user = User.objects.get(email=email, email_confirmed=False)
                except User.DoesNotExist as e:
                    user = None

                if user:  # registered before but not confirmed
                    user = user.update_password(password)
                else:
                    user = User.register_user(email, password)
                user.send_email_confirm(request)
                return responses.SuccessResponse({}).send()
        except (authnz_exceptions.CustomException, exceptions.ValidationError) as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()


@decorators.authentication_classes([])
@decorators.permission_classes([])
class UserLoginEmailView(generics.CreateAPIView):
    """
    post:

        Main Login with email & password

            email min 5, max 50

            password min 5, max 50

    """
    serializer_class = authnz_serializers.RegisterLoginEmailSerializer

    def post(self, request):
        try:
            serialized_data = self.serializer_class(data=request.data)
            if serialized_data.is_valid(raise_exception=True):
                email = serialized_data.data['email']
                password = serialized_data.data['password']
                try:
                    user = User.objects.get(email=email)
                except User.DoesNotExist as e:
                    raise authnz_exceptions.CustomException(detail=ugettext('You did not registered before.'))
                if user.email_confirmed and user.is_active and user.check_password(password):
                    user.save_last_login()
                    payload = jwt_payload_handler(user)  # todo: Is deprecated
                    jwt_token = utils.jwt_response_payload_handler(jwt_encode_handler(payload))
                    return responses.SuccessResponse(jwt_token).send()
                elif not user.email_confirmed:
                    try:
                        permissions.check_send_email_permission(email)
                    except authnz_exceptions.CustomException as e:
                        raise authnz_exceptions.CustomException(detail=ugettext('You did not confirm your email and you'
                                                                                ' reached max email sent, try later.'))
                    user.send_email_confirm(request)
                    raise authnz_exceptions.CustomException(detail=ugettext('You did not confirm your email,'
                                                                            ' We sent you a confirmation email'))
                elif not user.is_active:
                    raise authnz_exceptions.CustomException(detail=ugettext('Your account is not active,'
                                                                            ' please contact support.'))
                else:
                    raise authnz_exceptions.CustomException(detail=ugettext('Wrong login credentials.'))
        except (authnz_exceptions.CustomException, exceptions.ValidationError) as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class UserRefreshTokenView(generics.RetrieveAPIView):
    """
    get:

        Refresh JWT token
    """
    serializer_class = serializers.Serializer

    def get(self, request):
        try:
            if request.user.is_active:
                payload = jwt_payload_handler(request.user)  # todo: Is deprecated
                jwt_token = utils.jwt_response_payload_handler(jwt_encode_handler(payload))
                return responses.SuccessResponse(jwt_token).send()
            else:
                raise authnz_exceptions.CustomException(detail=_('This user is inactive, contact us.'))

        except authnz_exceptions.CustomException as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()


@decorators.authentication_classes([])
@decorators.permission_classes([])
class UserConfirmEmailView(generics.RetrieveAPIView):
    """
    get:

        Confirm email

            a link in confirm email
    """
    serializer_class = serializers.Serializer

    def get(self, request, uidb64, token):
        try:
            try:
                uid = urlsafe_base64_decode(uidb64).decode()
                user = User.objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                user = None

            if user is not None and email_activation_token.check_token(user, token):
                user.confirm_email()
                return render(request, 'authnz/mail_confirmed.html')
            else:
                return render(request, 'authnz/mail_confirm_invalid.html', status=400)

        except exceptions.ValidationError as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()
        except Exception as e:
            return responses.ErrorResponse(message=str(e)).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class UserMyProfileView(retrieve.RetrieveView, update.UpdateView):
    """
    get:

        my profile

    put:

        update profile

        first_name string min 5, max 50 allow blank for remove optional

        last_name string min 5, max 50  allow blank for remove optional


    patch:

        update profile

        first_name string min 5, max 50 allow blank for remove optional

        last_name string min 5, max 50  allow blank for remove optional

    """
    serializer_class = authnz_serializers.MyProfileSerializer
    model = User
