from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.tests_lists, name='tests_lists'),
    url(r'^test/(?P<pk>\d+)/$', views.test_detail, name='test_detail'),
    url(r'^test/(?P<test_id>\d+)/review/(?P<user_rate>(like)|(dislike))/$', views.review, name='review'),
    url(r'^test/new/$', views.test_new, name='test_new'),
    url(r'^test/(?P<pk>\d+)/edit/$', views.test_edit, name='test_edit'),
    url(r'^user/(?P<pk>\d+)/tests/$', views.user_tests, name='user_tests'),
    url(r'^test/(?P<pk>\d+)/publish/(?P<through_user_tests>(True)|(False))/$', views.test_publish, name='test_publish'),
    url(r'^test/(?P<pk>\d+)/test_unpublish/(?P<through_user_tests>(True)|(False))/$', views.test_unpublish, name='test_unpublish'),
    url(r'^test/(?P<pk>\d+)/make_ready/$', views.test_make_ready_for_passing, name='test_make_ready_for_passing'),
    url(r'^test/(?P<pk>\d+)/remove/(?P<through_user_tests>(True)|(False))/$', views.test_remove, name='test_remove'),
    url(r'^tests/$', views.tests, name='tests'),

    url(r'^test/(?P<test_id>\d+)/questions/$', views.questions_of_test, name='questions_of_test'),
    url(r'^test/(?P<test_id>\d+)/new_question/(?P<type>(closed)|(open)|(sequence)|(comparison))/$', views.new_question, name='new_question'),
    url(r'^test/(?P<test_id>\d+)/question/(?P<question_of_test_id>\d+)/edit/$', views.question_edit, name='question_edit'),
    url(r'^test/(?P<test_id>\d+)/question/(?P<question_of_test_id>\d+)/remove/$', views.question_remove, name='question_remove'),

    url(r'^test/(?P<test_id>\d+)/question/(?P<question_of_test_id>\d+)/add_options_or_elements/(?P<row>(left)|(right)|(none))$',
        views.new_options_or_elements, name='new_options_or_elements'),
    url(r'^test/(?P<test_id>\d+)/question/(?P<question_of_test_id>\d+)/options_or_elements_of_question_remove_all/$',
        views.options_or_elements_of_question_remove_all, name='options_or_elements_of_question_remove_all'),

    url(r'^test/(?P<pk>\d+)/passing/$', views.test_passing, name='test_passing'),    

    # url(r'^test/(?P<test_id>\d+)/question/(?P<question_of_test_id>\d+)/new_option/$', views.new_option, name='new_option'),

    url(r'^categories/$', views.categories, name='categories'),
    url(r'^tags/$', views.tags, name='tags'),

    #url(r'^categories_confirming/(?P<pk>\d+)/publish/$', permission_required("octapp.can_confirm")
    # (views.categories_confirming, name='categories_confirming')),

    #url(r'^test/(?P<pk>\d+)/comment/$', views.add_comment_to_test, name='add_comment_to_test'),
    #url(r'^comment/(?P<pk>\d+)/remove/$', views.comment_remove, name='comment_remove'),
]
