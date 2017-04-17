"""oct URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
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

class RegistrationViewTermOfServiceUniqueEmail(RegistrationView):
    form_class = RegistrationFormTermOfServiceUniqueEmail

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'', include('octapp.urls')),
    url(r'^avatar/', include('avatar.urls')),
    url(r'^accounts/logout/$', views.logout, name='auth_logout', kwargs={'next_page': '/'}),
    url(r'^accounts/login/$', views.login, name='auth_login'),
    url(r'^accounts/register/$', RegistrationViewTermOfServiceUniqueEmail.as_view(), name='registration_register'),
    url(r'^accounts/', include('registration.backends.simple.urls')),
    url(r'^accounts/', include('registration.auth_urls')),

    url(r'^ckeditor/upload/', login_required(ckeditor_views.upload), name='ckeditor_upload'),
    url(r'^ckeditor/browse/', never_cache(login_required(ckeditor_views.browse)), name='ckeditor_browse'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# ! only for developing
