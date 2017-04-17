from django.db import models
from django.utils import timezone
from ckeditor_uploader.fields import RichTextUploadingField
from ckeditor.fields import RichTextField

class Test(models.Model):
    author = models.ForeignKey('auth.User', related_name='tests', on_delete=models.CASCADE)
    category = models.ForeignKey('octapp.Category', related_name='tests', on_delete=models.CASCADE)
    scale = models.ForeignKey('octapp.ResultScale', related_name='tests', on_delete=models.CASCADE)
    tag = models.ManyToManyField('octapp.Tag')

    name = models.CharField("Наименование теста", max_length=200, blank=False)
    description = RichTextUploadingField("Описание теста", default='Описание теста отсутствует...')
    controlling = models.BooleanField("Использование контроля прохождения теста", default=False)
    time_restricting = models.BooleanField("Ограничение времени прохождения теста", default=False)
    rating = models.IntegerField("Рейтинг теста", default=0)
    created_date = models.DateTimeField("Дата создания", default=timezone.now)
    published_date = models.DateTimeField("Дата публикации", blank=True, null=True)

    def publish_test(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тест"
        verbose_name_plural = "Тесты"

class Comment(models.Model):
    test = models.ForeignKey('octapp.test', related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey('auth.User', related_name='comments')
    content = RichTextField("Содержимое комментария", blank=False)
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        self.content

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

class Category(models.Model):
    name = models.CharField("Наименование категории", max_length=120, blank=False)
    confirmed = models.BooleanField("Категория подтверждена", default=False)

    def confirm(self):
        self.confirmed = True
        self.save()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

class ResultScale(models.Model):
    name = models.CharField("Наименование шкалы", max_length=70, blank=False)
    scale_divisions_amount = models.IntegerField("Количество делений оценочной шкалы", default=0)
    # Доля в процентах каждого деления через запятую без пробелов, например, для 2-бальной шкалы (зачтено, незачтено)
    # разметка делений может быть "40,60"
    divisions_layout = models.CharField(
        "Разметка делений шкалы",
    max_length=20, blank=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Оценочная шкала"
        verbose_name_plural = "Оценочные шкалы"

class Tag(models.Model):
    name = models.CharField("Наименование тега", max_length=40, blank=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        