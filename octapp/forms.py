from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from registration import validators
from registration.forms import RegistrationFormTermsOfService
from ckeditor.widgets import CKEditorWidget
from .models import Test, Comment

User = get_user_model()

class RegistrationFormTermOfServiceUniqueEmail(RegistrationFormTermsOfService):
    user_manual = forms.BooleanField(
        widget=forms.CheckboxInput,
        label=(u'Я прочитал(а) инструкцию пользователя'),
        required=True
    )

    def clean_email(self):
        if User.objects.filter(email__iexact=self.cleaned_data['email']):
            raise forms.ValidationError(validators.DUPLICATE_EMAIL)
        return self.cleaned_data['email']

class TestForm(forms.ModelForm):
    publish_after_adding = forms.BooleanField(
        widget=forms.CheckboxInput,
        label=(u'Опубликовать тест сразу после отправки (загрузки) теста'),
        required=False
    )
    class Meta:
        model = Test
        fields = ('category', 'result_scale', 'tags', 'name', 'description', 'controlling', 'time_restricting')
