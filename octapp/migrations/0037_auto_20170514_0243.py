# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-13 19:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('octapp', '0036_auto_20170511_2123'),
    ]

    operations = [
        migrations.AddField(
            model_name='test',
            name='show_answers',
            field=models.BooleanField(default=True, verbose_name='Показывать ответы после прохождения'),
        ),
        migrations.AddField(
            model_name='test',
            name='single_passing',
            field=models.BooleanField(default=False, verbose_name='Допускается пройти тест только один раз'),
        ),
    ]