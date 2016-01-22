from django.conf.urls import url
from djqscsv_tests import views

urlpatterns = (
    url(r'^$', views.get_csv, name='get_csv'),
)
