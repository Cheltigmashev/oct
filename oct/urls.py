from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views
from django.conf import settings
from django.conf.urls.static import static
from registration.backends.simple.views import RegistrationView
from octapp.forms import RegistrationFormTermOfServiceUniqueEmail

from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from ckeditor_uploader import views as ckeditor_views

from django.utils import timezone
from octapp.models import Test
# Эта функция, также используемая для представления главной страницы, 
# будет передавать данные в контекст (в extra_context) стандартного представления для авторизации
from octapp.views import get_tests_lists_context

class RegistrationViewTermOfServiceUniqueEmail(RegistrationView):
    form_class = RegistrationFormTermOfServiceUniqueEmail


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'', include('octapp.urls')),
    url(r'^avatar/', include('avatar.urls')),
    url(r'^accounts/logout/$', views.logout, name='auth_logout', kwargs={'next_page': '/'}),
    # Отправляем переменные из представления главной страницы (tests_lists) в дополнительный контекст представления login
    url(r'^accounts/login/$', views.login, {'template_name': 'octapp/tests_lists.html',
    'extra_context': get_tests_lists_context()}, name='auth_login'),
    url(r'^accounts/register/$', RegistrationViewTermOfServiceUniqueEmail.as_view(), name='registration_register'),
    url(r'^accounts/', include('registration.backends.simple.urls')),
    url(r'^accounts/', include('registration.auth_urls')),
    url(r'^ckeditor/upload/', login_required(ckeditor_views.upload), name='ckeditor_upload'),
    url(r'^ckeditor/browse/', never_cache(login_required(ckeditor_views.browse)), name='ckeditor_browse'),
]

try:
    from .local_urls import statics
    urlpatterns += statics
except ImportError:
    pass