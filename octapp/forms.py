from django import forms
from django.contrib.auth import get_user_model
from django.forms import CheckboxSelectMultiple, NumberInput, TextInput
from .models import Category, ClosedQuestion, OpenQuestion, SequenceQuestion, ComparisonQuestion, ClosedQuestionOption, SequenceQuestionElement, ComparisonQuestionElement
from registration import validators
from registration.forms import RegistrationFormTermsOfService
from .models import Test, Comment
from ckeditor.widgets import CKEditorWidget

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
    # Фильтрация предложенных для выбора категорий
    def __init__(self, *args, **kwargs):
        super(TestForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(confirmed=True)

    new_category = forms.CharField(
        label=(u'Можете указать новую категорию'),
        required=False,
        help_text=(u'Учтите, что новая категория не будет использована, пока не будет подтверждена администратором или модератором'),
        widget=TextInput(attrs={'class': 'form-control', 'maxlength': 80,
            'title': 'Допускается использовать строчные и заглавные буквы, цифры, дефис и /',
            'placeholder': 'Допускается использовать строчные и заглавные буквы, цифры, дефис и /',
            'pattern': '[ a-zA-Zа-яёА-ЯЁ0-9 -/]+'}),
        error_messages={'unique': "Такая категория уже существует, выберите ее из предложенных."}
    )

    new_tags = forms.CharField(
        label=(u'Если требуется, укажите через запятую новые теги'),
        required=False,
        widget=TextInput(attrs={'maxlength': 250, 'class': 'form-control',
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
                  'description', 'controlling', 'time_restricting', 'anonymous_loader', 'show_answers', 'single_passing', 'only_registered_can_pass')
        # Переопределение стандартного виджета, подробнее на https://djbook.ru/rel1.9/topics/forms/modelforms.html#overriding-the-default-fields
        widgets = {
            'tags': CheckboxSelectMultiple,
            'time_restricting': NumberInput(attrs={'min': 1, 'placeholder': 'Не менее 1 минуты', 'class': 'form-control'}),
            'name': TextInput(attrs={'maxlength': 200, 'class': 'form-control',
                                     'title': 'Первая буква названия будет преобразована в заглавную, остальные — в строчные. Допускается использовать: буквы, цифры, пробелы, запятые, -/«»():;',
                                     'placeholder': 'Допускается использовать: буквы, цифры, пробелы, запятые, -/«»():;',
                                     'pattern': '[a-zA-Zа-яёА-Я0-9 -/,«»();:]*'}),
        }
        error_messages = {
            'name': {
                'unique': "Тест с таким именем уже присутствует в системе. Пожалуйста, придумайте другое название.",
            }
        }

# Формы для вопросов

class ClosedQuestionForm(forms.ModelForm):
    question_index_number = forms.IntegerField(
        label=(u'Можете указать другой порядковый номер вопроса'),
        required=False,
        help_text=(u'Порядковый номер другого вопроса изменится соответственно. Если введенный номер больше номера последнего вопроса, то будет считаться, что введен номер последнего.'),
        widget=NumberInput(attrs={'class': 'form-control', 'min': 1}),
    )
    
    add_options = forms.BooleanField(
        label=(u'Добавить вместе с вариантами ответа'),
        required=False,
        help_text=(u'Введите после содержимого самого вопроса (с новой строки, используя enter) слово "ВАРИАНТЫ", затем вновь перенос строки, а затем один или более вариантов ответа, разделяя их переносами строк (используйте enter, кнопка «Источник» должна быть неактивной. Минимум 2 варианта/элемента.')
    )

    class Meta:
        model = ClosedQuestion
        fields = ('question_content',
                  'correct_option_numbers')

        widgets = {
            'correct_option_numbers': TextInput(attrs={'maxlength': 55, 'class': 'form-control',
                                                       'placeholder': 'Допустимы цифры, запятые и пробел в формате 1, 2, 3',
                                                       'pattern': '(?:\d+(?:,\s)?)+'}),
        }

class OpenQuestionForm(forms.ModelForm):
    question_index_number = forms.IntegerField(
        label=(u'Можете указать другой порядковый номер вопроса'),
        required=False,
        help_text=(u'Порядковый номер другого вопроса изменится соответственно. Если введенный номер больше номера последнего вопроса, то будет считаться, что введен номер последнего.'),
        widget=NumberInput(attrs={'class': 'form-control', 'min': 1}),
    )

    class Meta:
        model = OpenQuestion
        fields = ('question_content_before_blank',
                  'question_content_after_blank',
                  'correct_option')

        widgets = {
            'correct_option': TextInput(attrs={'maxlength': 120, 'class': 'form-control'}),
        }

class SequenceQuestionForm(forms.ModelForm):
    question_index_number = forms.IntegerField(
        label=(u'Можете указать другой порядковый номер вопроса'),
        required=False,
        help_text=(u'Порядковый номер другого вопроса изменится соответственно. Если введенный номер больше номера последнего вопроса, то будет считаться, что введен номер последнего.'),
        widget=NumberInput(attrs={'class': 'form-control', 'min': 1}),
    )

    add_sequ_elements = forms.BooleanField(
        label=(u'Добавить вместе с элементами последовательности'),
        required=False,
        help_text=(u'Введите после содержимого самого вопроса (с новой строки, используя enter) слово "ЭЛЕМЕНТЫ", затем вновь перенос строки, а затем один или более элементов последовательности, разделяя их переносами строк (используйте enter, кнопка «Источник» должна быть неактивной. Минимум 2 варианта/элемента.')
    )

    class Meta:
        model = SequenceQuestion
        fields = ('sequence_question_content',
                  'correct_sequence')

        widgets = {
            'correct_sequence': TextInput(attrs={'maxlength': 70, 'class': 'form-control',
                                                       'placeholder': 'Допустимы цифры, запятые и пробел в формате 1, 2, 3',
                                                       'pattern': '(?:\d+(?:,\s)?)+'}),
        }

class ComparisonQuestionForm(forms.ModelForm):
    question_index_number = forms.IntegerField(
        label=(u'Можете указать другой порядковый номер вопроса'),
        required=False,
        help_text=(u'Порядковый номер другого вопроса изменится соответственно. Если введенный номер больше номера последнего вопроса, то будет считаться, что введен номер последнего.'),
        widget=NumberInput(attrs={'class': 'form-control', 'min': 1}),
    )

    add_comp_elements = forms.BooleanField(
        label=(u'Добавить вместе с элементами рядов'),
        required=False,
        help_text=(u'Введите после содержимого самого вопроса (с новой строки, используя enter) слово «СЛЕВА», затем вновь перенос строки, а затем один или более элементов ЛЕВОГО ряда сопоставления, разделяя их переносами строк (используйте enter, кнопка «Источник» должна быть неактивной. Аналогично можете ввести элементы ПРАВОГО ряда, используя строку-разделитель «СПРАВА». Минимум 2 варианта/элемента.')
    )

    class Meta:
        model = ComparisonQuestion
        fields = ('comparison_question_content',
                  'correct_sequence')

        widgets = {
            'correct_sequence': TextInput(attrs={'maxlength': 55, 'class': 'form-control',
                                                       'placeholder': 'Допустимы цифры, запятые, дефис и пробел',
                                                       'pattern': '(?:[0-9]*-[0-9]*(?:, )?)+'}),
        }

# Формы для вариантов ответа либо элементов последовательности/сопоставления
class ClosedQuestionOptionForm(forms.ModelForm):
    add_several = forms.BooleanField(
        label=(u'Добавить несколько'),
        required=False,
        help_text=(u'Для разделения вариантов ответа используйте переносы строк (enter, каждый параграф станет отдельным вариантом). Кнопка «Источник» должна быть при этом неактивной.')
    )

    class Meta:
        model = ClosedQuestionOption
        fields = ('content',
                  'option_number')

        widgets = {
            'option_number': NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }


class SequenceQuestionElementForm(forms.ModelForm):
    add_several = forms.BooleanField(
        label=(u'Добавить несколько'),
        required=False,
        help_text=(u'Для разделения элементов последовательности используйте переносы строк (enter, каждый параграф станет отдельным элементом). Кнопка «Источник» должна быть при этом неактивной.')
    )

    class Meta:
        model = SequenceQuestionElement
        fields = ('element_content',
                  'element_index_number')

        widgets = {
            'element_index_number': NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

class ComparisonQuestionElementForm(forms.ModelForm):
    add_several = forms.BooleanField(
        label=(u'Добавить несколько'),
        required=False,
        help_text=(u'Для разделения элементов левого или правого ряда сопоставления используйте переносы строк (enter, каждый параграф станет отдельным элементом). Кнопка «Источник» должна быть при этом неактивной.')
    )

    class Meta:
        model = ComparisonQuestionElement
        fields = ('element_content',
                  'element_index_number')

        widgets = {
            'element_index_number': NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }
