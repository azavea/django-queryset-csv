from django.conf.urls import patterns, include, url
import views

urlpatterns = patterns(
    '',
    url(r'^get_csv/', views.get_csv, name='get_csv'),
)
