from django.urls import path
from djqscsv_tests import views

urlpatterns = (
    path('', views.get_csv, name='get_csv'),
)
