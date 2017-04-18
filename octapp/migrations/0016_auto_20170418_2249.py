# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-18 15:49
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('octapp', '0015_auto_20170418_2225'),
    ]

    operations = [
        migrations.AlterField(
            model_name='test',
            name='author',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tests', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь, загрузивший тест'),
        ),
        migrations.AlterField(
            model_name='test',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tests', to='octapp.Category', verbose_name='Категория теста'),
        ),
        migrations.AlterField(
            model_name='test',
            name='tags',
            field=models.ManyToManyField(blank=True, null=True, to='octapp.Tag', verbose_name='Тег или теги теста'),
        ),
    ]
