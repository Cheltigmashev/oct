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
    name = models.CharField('Наименование теста', max_length=200, blank=False, unique=True)
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
        
class Test_rate(models.Model):
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
    test = models.ForeignKey('octapp.Test', related_name='closed_questions', on_delete=models.CASCADE,
                             verbose_name='Тест, к которому относится вопрос', null=False, blank=False)
    only_one_right = models.BooleanField('Только один вариант ответа — правильный', default=True, blank=True)
    question_content = RichTextField('Содержимое (наполнение, контент) вопроса.', null=False,
        blank=False, help_text='Используйте сервисы хранения изображений, если требуется добавить картинку.')
    question_index_number = models.IntegerField('Порядковый номер вопроса в тесте', blank=False, null=False)
    correct_option_numbers = models.CharField('Номера одного или нескольких правильных вариантов через запятую и без пробелов',
        max_length=55, blank=False, null=False)

    def __str__(self):
        return self.test.name + ':' + self.question_index_number + '(закрытый)'

    class Meta:
        ordering = ['test']
        verbose_name = 'Вопрос закрытого типа'
        verbose_name_plural = 'Вопросы закрытого типа'

class OpenQuestion(models.Model):
    test = models.ForeignKey('octapp.Test', related_name='open_questions', on_delete=models.CASCADE,
                             null=False, blank=False, verbose_name='Тест, к которому относится вопрос')
    question_content_before_blank = RichTextField('Содержимое (наполнение, контент) вопроса перед пропуском', null=False, blank=False)
    question_content_after_blank = RichTextField('Содержимое (наполнение, контент) вопроса после пропуска (может отсутствовать)', null=True, blank=True)
    correct_option = models.CharField('Текст правильного ответа', max_length=120, blank=False, null=False)
    question_index_number = models.IntegerField('Порядковый номер вопроса в тесте', blank=False, null=False)

    def __str__(self):
        return self.test.name + ':' + self.question_index_number + '(открытый)'

    class Meta:
        ordering = ['test']
        verbose_name = 'Вопрос открытого типа'
        verbose_name_plural = 'Вопросы открытого типа'

class SequenceQuestion(models.Model):
    test = models.ForeignKey('octapp.Test', related_name='sequence_questions', null=False, blank=False,
                on_delete=models.CASCADE, verbose_name='Тест, к которому относится вопрос')
    question_content = RichTextField('Содержимое (наполнение, контент) вопроса', null=False, blank=False)
    correct_sequence = models.CharField(
        'Правильная последовательность',
        max_length=55, blank=False, null=False, help_text='Номера элементов последовательности, разделенные запятыми без пробелов.')
    question_index_number = models.IntegerField('Порядковый номер вопроса в тесте', blank=False, null=False)

    def __str__(self):
        return self.test.name + ':' + self.question_index_number + '(последовательность)'

    class Meta:
        ordering = ['test']
        verbose_name = 'Вопрос на определение последовательности (порядка) элементов'
        verbose_name_plural = 'Вопросы на определение последовательности (порядка) элементов'

class SequenceQuestionElement(models.Model):
    sequence_question = models.ForeignKey('octapp.SequenceQuestion', related_name='sequence_elements',
        on_delete=models.CASCADE, verbose_name='Вопрос на определение последовательности, к которому относится элемент')
    element_index_number = models.IntegerField('Порядковый номер элемента последовательности', blank=False, null=False)

    def __str__(self):
        return 'Элемент №' + str(self.element_index_number) + \
               ' вопроса № ' + self.sequence_question.question_index_number

    class Meta:
        ordering = ['element_index_number']
        verbose_name = 'Элемент для вопроса на определение последовательности'
        verbose_name_plural = 'Элементы для вопроса на определение последовательности'

class ComparisonQuestion(models.Model):
    test = models.ForeignKey('octapp.Test', related_name='comparison_questions', on_delete=models.CASCADE, verbose_name='Тест, к которому относится вопрос')
    question_content = RichTextField('Содержимое (наполнение, контент) вопроса', null=False, blank=False)
    correct_sequence = models.CharField(
        'Правильная последовательность элементов второго (правого) ряда (столбца)',
        max_length=55, blank=False, null=False, help_text='Номера элементов последовательности второго ряда, разделенные запятыми без пробелов.')
    question_index_number = models.IntegerField('Порядковый номер вопроса в тесте', blank=False, null=False)

    def __str__(self):
        return self.test.name + ':' + self.question_index_number + '(сопоставление)'

    class Meta:
        ordering = ['test']
        verbose_name = 'Вопрос на сопоставление'
        verbose_name_plural = 'Вопросы на сопоставление'
