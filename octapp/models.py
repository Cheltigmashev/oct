from django.db import models
from django.utils import timezone
from ckeditor_uploader.fields import RichTextUploadingField
from ckeditor.fields import RichTextField

class Test(models.Model):
    author = models.ForeignKey('auth.User', related_name='tests', on_delete=models.CASCADE, 
            verbose_name="Пользователь, загрузивший тест", null=True, blank=True)
    category = models.ForeignKey('octapp.Category', related_name='tests', on_delete=models.CASCADE, verbose_name="Категория теста", null=True, blank=True)
    result_scale = models.ForeignKey('octapp.ResultScale', related_name='tests', on_delete=models.CASCADE, verbose_name="Оценочная шкала теста")
    # id est test may contain many tags, and tags may be related to different tests
    # tagS name prefered by Django docs
    tags = models.ManyToManyField('octapp.Tag', verbose_name="Тег или теги теста", blank=True)

    name = models.CharField("Наименование теста", max_length=200, blank=False)
    description = RichTextUploadingField("Описание теста", default='Описание теста отсутствует...')
    controlling = models.BooleanField("Использование контроля прохождения теста", default=False)
    time_restricting = models.BooleanField("Ограничение времени прохождения теста", default=False)
    rating = models.IntegerField("Рейтинг теста", default=0, editable=False)
    created_date = models.DateTimeField("Дата создания", default=timezone.now, editable=False)
    published_date = models.DateTimeField("Дата публикации", blank=True, null=True, editable=False)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тест"
        verbose_name_plural = "Тесты"

class Comment(models.Model):
    test = models.ForeignKey('octapp.Test', related_name='comments', on_delete=models.CASCADE, verbose_name="Тест, к которому относится комментарий")
    author = models.ForeignKey('auth.User', related_name='comments', verbose_name="Пользователь-автор комментария")

    content = RichTextField("Содержимое комментария", blank=False)
    created_date = models.DateTimeField("Дата создания комментария", default=timezone.now)

    def __str__(self):
        self.content

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

class Category(models.Model):
    name = models.CharField("Наименование категории", max_length=120, blank=False, unique=True)
    confirmed = models.BooleanField("Категория подтверждена", default=False)

    def confirm(self):
        self.confirmed = True
        self.save()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        permissions = (
            ("confirm_category", "Can confirm_category"),
        )

class ResultScale(models.Model):
    name = models.CharField("Наименование шкалы", max_length=70, blank=False)
    scale_divisions_amount = models.IntegerField("Количество делений оценочной шкалы", default=0)
    
    divisions_layout = models.CharField(
        "Разметка делений шкалы -- процентные доли каждого деления через запятую",
    max_length=20, blank=False, help_text="например, для 2-бальной шкалы (зачтено, незачтено) разметка делений может быть <q>'40,60'</q>")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Оценочная шкала"
        verbose_name_plural = "Оценочные шкалы"

class Tag(models.Model):
    name = models.CharField("Наименование тега", max_length=40, blank=False, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        