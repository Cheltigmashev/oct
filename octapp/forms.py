from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.forms import CheckboxSelectMultiple
from django.forms import NumberInput
from django.forms import TextInput
from .models import Category

from registration import validators
from registration.forms import RegistrationFormTermsOfService
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
    def __init__(self, *args, **kwargs):
        super(TestForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(confirmed=True)

    new_category = forms.CharField(
        label=(u'Можете указать новую категорию'),
        required=False,
        help_text=(u'Учтите, что новая категория не будет использована, пока не будет подтверждена администратором или модератором'),
        widget=TextInput(attrs={'maxlength': 80, 'title': 'Допускается использовать строчные и заглавные буквы, цифры, дефис и /', 'placeholder': 'Допускается использовать строчные и заглавные буквы, цифры, дефис и /', 'pattern': '[ a-zA-Zа-яёА-ЯЁ0-9 -/]+'}),
        error_messages={'unique': "Такая категория уже существует, выберите ее из предложенных."}
    )

    new_tags = forms.CharField(
        label=(u'Если требуется, укажите через запятую новые теги'),
        required=False,
        widget=TextInput(attrs={'maxlength': 250,
                                'title': 'Допускается использовать строчные и заглавные буквы, цифры, запятые, дефис и /',
                                'placeholder': 'Допускается использовать строчные и заглавные буквы, цифры, запятые, дефис и /',
                                'pattern': '[a-zA-Zа-яёА-ЯЁ0-9 -/,]+'}),
        error_messages={'unique': "Такой тег уже существует, выберите его из предложенных."}
    )

    publish_after_adding = forms.BooleanField(
        widget=forms.CheckboxInput,
        label=(u'Опубликовать тест сразу после отправки (загрузки) либо редактирования теста'),
        required=False
    )

    class Meta:
        model = Test
        fields = ('category', 'result_scale', 'tags', 'name',
                  'description', 'controlling', 'time_restricting', 'anonymous_loader')
        # Переопределение стандартного виджета, подробнее на https://djbook.ru/rel1.9/topics/forms/modelforms.html#overriding-the-default-fields
        widgets = {
            'tags': CheckboxSelectMultiple,
            'time_restricting': NumberInput(attrs={'min': 1, 'placeholder': 'Не менее 1 минуты'}),
            'name': TextInput(attrs={'maxlength': 200, 'title': 'Первая буква названия будет преобразована в заглавную, остальные — в строчные. Допускается использовать: буквы, цифры, пробелы, запятые, -/«»():;', 'placeholder': 'Допускается использовать: буквы, цифры, пробелы, запятые, -/«»():;', 'pattern': '[a-zA-Zа-яёА-Я0-9 -/,«»();:]*'}),
        }
        error_messages = {
            'name': {
                'unique': "Тест с таким именем уже присутствует в системе. Пожалуйста, придумайте другое название.",
            }
        }
