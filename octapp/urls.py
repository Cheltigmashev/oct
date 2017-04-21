from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.tests_lists, name='tests_lists'),
    url(r'^test/(?P<pk>\d+)/$', views.test_detail, name='test_detail'),
    url(r'^test/(?P<test_id>\d+)/user/(?P<user_id>\d+)/review/(?P<user_rate>(like)|(dislike))/$', views.review, name='review'),
    url(r'^test/new/$', views.test_new, name='test_new'),
    url(r'^test/(?P<pk>\d+)/edit/$', views.test_edit, name='test_edit'),
    url(r'^user/(?P<pk>\d+)/tests/$', views.user_tests, name='user_tests'),
    url(r'^test/(?P<pk>\d+)/publish/$', views.test_publish, name='test_publish'),
    url(r'^test/(?P<pk>\d+)/make_ready/$', views.test_make_ready_for_passing, name='test_make_ready_for_passing'),
    url(r'^test/(?P<pk>\d+)/remove/$', views.test_remove, name='test_remove'),
    url(r'^test/(?P<pk>\d+)/test_remove_through_user_tests/$', views.test_remove_through_user_tests, name='test_remove_through_user_tests'),

    #url(r'^categories_confirming/(?P<pk>\d+)/publish/$', permission_required("octapp.can_confirm")
    # (views.categories_confirming, name='categories_confirming')),

    #url(r'^test/(?P<pk>\d+)/comment/$', views.add_comment_to_test, name='add_comment_to_test'),
    #url(r'^comment/(?P<pk>\d+)/remove/$', views.comment_remove, name='comment_remove'),
]
