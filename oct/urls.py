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
from octapp.views import tests_lists

#https://djbook.ru/forum/topic/2366/
from registration.backends.model_activation.views import RegistrationView
from registration.forms import RegistrationFormUniqueEmail

# view с формой, проверяющей email на уникальность
class RegistrationViewUniqueEmail(RegistrationView):
    form_class = RegistrationFormUniqueEmail


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'', include('octapp.urls')),

    #https://djbook.ru/forum/topic/2366/
    url(r'^accounts/register/$', RegistrationViewUniqueEmail.as_view(), name='registration_register'),

    url(r'^accounts/logout/$', views.logout, name='auth_logout', kwargs={'next_page': '/'}),
    url(r'^accounts/login/$', views.login, name='auth_login'),

    url(r'^accounts/', include('registration.backends.hmac.urls')),
    url(r'^accounts/', include('registration.auth_urls')),
]
