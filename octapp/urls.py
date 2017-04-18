from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.tests_lists, name='tests_lists'),

    #url(r'^user/(?P<pk>[0-9]+)/tests/$', views.user_tests, name='user_tests'),

    url(r'^test/(?P<pk>[0-9]+)/$', views.test_detail, name='test_detail'),
    url(r'^test/new/$', views.test_new, name='test_new'),
    url(r'^test/(?P<pk>[0-9]+)/edit/$', views.test_edit, name='test_edit'),
    
    #url(r'^test/(?P<pk>\d+)/publish/$', views.test_publish, name='test_publish'),

    #url(r'^test/(?P<pk>\d+)/comment/$', views.add_comment_to_test, name='add_comment_to_test'),
    #url(r'^comment/(?P<pk>\d+)/remove/$', views.comment_remove, name='comment_remove'),

    #url(r'^categories_confirming/(?P<pk>\d+)/publish/$', permission_required("octapp.can_confirm")
    # (views.categories_confirming, name='categories_confirming')),
]
