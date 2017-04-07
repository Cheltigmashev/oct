from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.tests_lists, name='tests_lists'),
]
