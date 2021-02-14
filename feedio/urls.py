from django.conf import settings
from django.contrib import admin
from django.urls import path, re_path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from authnz import urls as authnz_urls
from feed import urls as feed_urls


schema_view = get_schema_view(
   openapi.Info(
      title="Feedio API",
      default_version='v1'
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(authnz_urls)),
    path('', include(feed_urls)),
]

if settings.DEBUG:
    urlpatterns.append(
        re_path('^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    )
