from django.urls import path

from utils import views as utils_views


urlpatterns = [
    path('utils_views/data_test/', utils_views.CreateDataTestView.as_view()),
]
