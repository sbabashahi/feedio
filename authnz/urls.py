from django.urls import path, re_path

from authnz import views as authnz_views


urlpatterns = [
    path('authnz/register_email/', authnz_views.UserRegisterEmailView.as_view()),
    path('authnz/login_email/', authnz_views.UserLoginEmailView.as_view()),
    path('authnz/refresh_my_token/', authnz_views.UserRefreshTokenView.as_view()),
    path('authnz/my_profile/', authnz_views.UserMyProfileView.as_view()),
    re_path('^authnz/approve_email/(?P<uidb64>[0-9A-Za-z_\-\']+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,32})/$',
        authnz_views.UserConfirmEmailView.as_view(), name='approve_email'),
    ]
