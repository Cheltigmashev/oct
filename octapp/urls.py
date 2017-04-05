from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.tests_list, name='tests_list'),
]
