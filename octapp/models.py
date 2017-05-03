from django.db import models
from django.utils import timezone
from ckeditor_uploader.fields import RichTextUploadingField
from ckeditor.fields import RichTextField

class Test(models.Model):
    author = models.ForeignKey('auth.User', related_name='tests', on_delete=models.CASCADE, 
            verbose_name='Пользователь, загрузивший тест', null=True, blank=True)
    category = models.ForeignKey('octapp.Category', related_name='tests', on_delete=models.CASCADE, verbose_name='Категория теста', null=True, blank=True)
    result_scale = models.ForeignKey('octapp.ResultScale', related_name='tests', on_delete=models.CASCADE, verbose_name='Оценочная шкала теста')
    # Т.е. тесту может быть назначено много тегов, а теги
    # могут быть назначены для  разных тестов
    # По документации Django, предпочтительно использовать имя поля во множ. числе
    tags = models.ManyToManyField('octapp.Tag', related_name='tests', verbose_name='Тег или теги теста', blank=True)

    anonymous_loader = models.BooleanField('Анонимный тест. На странице теста не будет указан пользователь, который загрузил тест.', default=False, blank=True)
    name = models.CharField('Наименование теста', max_length=200, null=False, blank=False, unique=True)
    description = RichTextUploadingField('Описание теста', default='Описание теста отсутствует...')
    controlling = models.BooleanField('Использование контроля прохождения теста', default=False)
    time_restricting = models.IntegerField('Ограничение времени прохождения теста в минутах', null=True, blank=True)
    rating = models.IntegerField('Рейтинг теста', default=0, editable=False)
    created_date = models.DateTimeField('Дата создания', default=timezone.now, editable=False)
    published_date = models.DateTimeField('Дата публикации', blank=True, null=True, editable=False)
    ready_for_passing = models.BooleanField('Готовность теста для прохождения другими пользователями', default=False, blank=True, editable=False)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def unpublish(self):
        self.published_date = None
        self.save()

    def make_ready_for_passing(self):
        self.ready_for_passing = True
        self.save()

    def review_positively(self):
        self.rating += 1
        self.save()

    def review_negatively(self):
        self.rating -= 1
        self.save()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Тест'
        verbose_name_plural = 'Тесты'

class Comment(models.Model):
    test = models.ForeignKey('octapp.Test', related_name='comments', on_delete=models.CASCADE, verbose_name='Тест, к которому относится комментарий')
    author = models.ForeignKey('auth.User', related_name='comments', verbose_name='Пользователь-автор комментария')

    content = RichTextField('Содержимое (наполнение, контент) комментария',
                    help_text='Используйте сервисы хранения изображений, если требуется добавить картинку.', blank=False)
    created_date = models.DateTimeField('Дата создания комментария', default=timezone.now)

    def __str__(self):
        return 'Комментарий пользователя «' + self.author.username + '» к тесту ' + self.test.name

    class Meta:
        ordering = ['created_date']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

class Category(models.Model):
    name = models.CharField('Наименование категории', max_length=80, blank=False, unique=True)
    confirmed = models.BooleanField('Категория подтверждена', default=False)

    def confirm(self):
        self.confirmed = True
        self.save()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        permissions = (
            ('confirm_category', 'Can confirm_category'),
        )

class ResultScale(models.Model):
    name = models.CharField('Наименование шкалы', max_length=70, blank=False, unique=True)
    scale_divisions_amount = models.IntegerField('Количество возможных оценок', default=0)
    
    divisions_layout = models.CharField(
        'Разметка делений шкалы -- процентные доли каждого деления через запятую',
    max_length=80, blank=False, help_text='Следует указать [количество возможных баллов/оценок - 1] элементов. Например, для 2-бальной шкалы (зачтено, незачтено) разметка делений может быть <q>50</q>')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Оценочная шкала'
        verbose_name_plural = 'Оценочные шкалы'

class Tag(models.Model):
    name = models.CharField('Наименование тега', max_length=40, blank=False, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        
class TestRate(models.Model):
    test = models.ForeignKey('octapp.Test',
            related_name='rates',
            on_delete=models.CASCADE,
            verbose_name='Тест, к которому относится данная пользовательская оценка (рейтинг)',
            null=False, blank=False)
    reviewer = models.ForeignKey('auth.User', related_name='rates', 
            verbose_name='Пользователь, к которому относится данная пользовательская оценка (рейтинг)',
            null=False, blank=False)
    like = models.BooleanField('Тест понравился? Если True — +1 к рейтингу, иначе — -1 к рейтингу',
            null=False, blank=False)

    def __str__(self):
        if self.like:
            rate = '+1'
        else:
            rate = '-1'
        return rate + ' от пользователя ' + self.reviewer.username

    class Meta:
        verbose_name = 'Оценка тестов'
        verbose_name_plural = 'Оценки тестов'

# Модели вопросов разных типов

class ClosedQuestion(models.Model):
    question_of_test = models.OneToOneField('octapp.QuestionOfTest', related_name='closed_question', null=True,
            blank=False, on_delete=models.CASCADE, verbose_name='Нумерованный элемент (пункт) списка вопросов')
    only_one_right = models.BooleanField('Только один вариант ответа — правильный', default=True, blank=True)
    question_content = RichTextField('Содержимое (наполнение, контент) вопроса.', null=False,
        blank=False, help_text='Используйте сервисы хранения изображений, если требуется добавить картинку.', default='')
    correct_option_numbers = models.CharField('Номера одного или нескольких правильных вариантов через запятую и без пробелов',
        max_length=55, blank=False, null=False)

    def __str__(self):
        return self.question_of_test.test.name + ':' + self.question_of_test.question_index_number + ' (закрытый)'

    class Meta:
        ordering = ['question_of_test']
        verbose_name = 'Вопрос закрытого типа'
        verbose_name_plural = 'Вопросы закрытого типа'

class ClosedQuestionOption(models.Model):
    question = models.ForeignKey('octapp.ClosedQuestion', related_name='closed_question_options',
        blank=False, on_delete=models.CASCADE,
        verbose_name='Вопрос закрытого типа, которому принадлежит данный вариант ответа')
    content = RichTextField('Содержимое (наполнение, контент) варианта ответа',
                            help_text='Используйте сервисы хранения изображений, если требуется добавить картинку.',
                            null=False, blank=False, default='')
    option_number = models.IntegerField('Порядковый номер варианта ответа на вопрос закр. типа', blank=False, null=False)

    def __str__(self):
        return 'Вариант ответа № ' + str(self.option_number) + ' на вопрос № /' + self.question.question_of_test.question_index_number + '/'

    class Meta:
        ordering = ['question']
        verbose_name = 'Вариант ответа на вопрос закрытого типа'
        verbose_name_plural = 'Варианты ответа на вопрос закрытого типа'

class OpenQuestion(models.Model):
    question_of_test = models.OneToOneField('octapp.QuestionOfTest', related_name='open_question', null=True,
        blank=False, on_delete=models.CASCADE, verbose_name='Нумерованный элемент (пункт) списка вопросов')
    question_content_before_blank = RichTextField('Содержимое (наполнение, контент) вопроса перед пропуском',
          help_text='Используйте сервисы хранения изображений, если требуется добавить картинку.',
          null=False, blank=False, default='')
    question_content_after_blank = RichTextField('Содержимое (наполнение, контент) вопроса после пропуска (может отсутствовать)',
             help_text='Используйте сервисы хранения изображений, если требуется добавить картинку.',
             null=False, blank=False, default='')
    # При обработке результатов прохождения, регистр учитываться не должен
    correct_option = models.CharField('Текст правильного ответа', max_length=120, blank=False, null=False)

    def __str__(self):
        return self.question_of_test.test.name + ':' + str(self.question_of_test.question_index_number) + ' (открытый)'

    class Meta:
        ordering = ['question_of_test']
        verbose_name = 'Вопрос открытого типа'
        verbose_name_plural = 'Вопросы открытого типа'

class SequenceQuestion(models.Model):
    # null=True пришлось добавлять, чтобы создать миграцию
    question_of_test = models.OneToOneField('octapp.QuestionOfTest', related_name='sequence_question', null=True,
        blank=False, on_delete=models.CASCADE, verbose_name='Нумерованный элемент (пункт) списка вопросов')
    question_content = RichTextField('Содержимое (наполнение, контент) вопроса',
                                     help_text='Используйте сервисы хранения изображений, если требуется добавить картинку.',
                                     null=False, blank=False, default='')
    correct_sequence = models.CharField(
        'Правильная последовательность',
        max_length=70, blank=False, null=False, help_text='Номера элементов последовательности, разделенные запятыми без пробелов.')

    def __str__(self):
        return self.question_of_test.test.name + ':' + str(self.question_of_test.question_index_number) + ' (последовательность)'

    class Meta:
        ordering = ['question_of_test']
        verbose_name = 'Вопрос на определение последовательности (порядка) элементов'
        verbose_name_plural = 'Вопросы на определение последовательности (порядка) элементов'

class SequenceQuestionElement(models.Model):
    question = models.ForeignKey('octapp.SequenceQuestion', related_name='sequence_elements', blank=False,
        on_delete=models.CASCADE, verbose_name='Вопрос на определение последовательности, к которому относится элемент')
    element_content = RichTextField('Содержимое (наполнение, контент) элемента последовательности',
                                     help_text='Используйте сервисы хранения изображений, если требуется добавить картинку.',
                                     null=False, blank=False, default='')
    element_index_number = models.IntegerField('Порядковый номер элемента последовательности', blank=False, null=False)

    def __str__(self):
        return 'Элемент №' + str(self.element_index_number) + \
               ' вопроса № ' + self.question.question_of_test.question_index_number

    class Meta:
        ordering = ['question']
        verbose_name = 'Элемент для вопроса на определение последовательности'
        verbose_name_plural = 'Элементы для вопроса на определение последовательности'

class ComparisonQuestion(models.Model):
    question_of_test = models.OneToOneField('octapp.QuestionOfTest', related_name='comparison_question', null=True,
        blank=False, on_delete=models.CASCADE, verbose_name='Нумерованный элемент (пункт) списка вопросов')
    question_content = RichTextField('Содержимое (наполнение, контент) вопроса',
                                     help_text='Используйте сервисы хранения изображений, если требуется добавить картинку.',
                                     null=False, blank=False, default='')
    left_row_elements = models.ManyToManyField('octapp.ComparisonQuestionElement', related_name='left_comparison_elements',
        verbose_name='Левые элементы сопоставления', blank=False)
    right_row_elements = models.ManyToManyField('octapp.ComparisonQuestionElement', related_name='right_comparison_elements',
        verbose_name='Правые элементы сопоставления', blank=False)
    correct_sequence = models.CharField('Правильная последовательность элементов второго (правого) ряда (столбца)',
        max_length=55, blank=False, null=False, help_text='Номера элементов последовательности второго ряда, разделенные запятыми без пробелов.')

    def __str__(self):
        return self.question_of_test.test.name + ', вопрос № ' + self.question_of_test.question_index_number + ' (сопоставление)'

    class Meta:
        ordering = ['question_of_test']
        verbose_name = 'Вопрос на сопоставление'
        verbose_name_plural = 'Вопросы на сопоставление'

class ComparisonQuestionElement(models.Model):
    question = models.ForeignKey('octapp.ComparisonQuestion', related_name='comparison_elements',
        blank=False, on_delete=models.CASCADE, verbose_name='Вопрос на сопоставление, к которому относится элемент')
    element_content = RichTextField('Содержимое (наполнение, контент) элемента сопоставления',
                                     help_text='Используйте сервисы хранения изображений, если требуется добавить картинку.',
                                     null=False, blank=False, default='')
    element_index_number = models.IntegerField('Порядковый номер элемента сопоставления', blank=False, null=False)

    def __str__(self):
        return 'Элемент № ' + str(self.element_index_number) + \
               ' вопроса /' + self.question.question_of_test.test.name + '/'

    class Meta:
        ordering = ['question']
        verbose_name = 'Элемент левого или правого ряда в вопросе на сопоставление'
        verbose_name_plural = 'Элементы левого или правого ряда в вопросе на сопоставление'

class QuestionOfTest(models.Model):
    test = models.ForeignKey('octapp.Test', related_name='questions_of_test',
            blank=False, on_delete=models.CASCADE, verbose_name='Тест, к которому относится вопрос')
    question_index_number = models.IntegerField('Порядковый номер вопроса в тесте', blank=False, null=False)
    type_of_question = models.CharField('Тип теста, чтобы знать, к какому типу вопроса обращаться через связь',
            max_length=7, blank=False, unique=True,
            choices=[('ClsdQ', 'закрытый'), ('OpndQ', 'открытый'),
                     ('SqncQ', 'последовательность'), ('CmprsnQ', 'сопоставление')])

    def __str__(self):
        return 'Вопрос № ' + str(self.element_index_number) + \
               ' теста № ' + self.test.name

    class Meta:
        ordering = ['test']
        verbose_name = 'Вопрос (как пункт) теста'
        verbose_name_plural = 'Вопросы (как пункт) теста'
