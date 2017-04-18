# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-18 10:29
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('octapp', '0006_auto_20170418_0004'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='author',
            field=models.ForeignKey(help_text='Пользователь-автор комментария', on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='comment',
            name='created_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата создания комментария'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='test',
            field=models.ForeignKey(help_text='Тест, к которому относится комментарий', on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='octapp.Test'),
        ),
        migrations.AlterField(
            model_name='test',
            name='author',
            field=models.ForeignKey(help_text='Пользователь, загрузивший тест', on_delete=django.db.models.deletion.CASCADE, related_name='tests', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='test',
            name='category',
            field=models.ForeignKey(help_text='Категория теста', on_delete=django.db.models.deletion.CASCADE, related_name='tests', to='octapp.Category'),
        ),
        migrations.AlterField(
            model_name='test',
            name='name',
            field=models.CharField(max_length=200, unique=True, verbose_name='Наименование теста'),
        ),
        migrations.AlterField(
            model_name='test',
            name='scale',
            field=models.ForeignKey(help_text='Оценочная шкала теста', on_delete=django.db.models.deletion.CASCADE, related_name='tests', to='octapp.ResultScale'),
        ),
        migrations.AlterField(
            model_name='test',
            name='tag',
            field=models.ManyToManyField(help_text='Тег или теги теста', to='octapp.Tag'),
        ),
    ]
