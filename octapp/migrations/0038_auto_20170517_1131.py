# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-17 04:31
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('octapp', '0037_auto_20170514_0243'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='result',
            options={'ordering': ['user', 'test'], 'verbose_name': 'Результат прохождения теста', 'verbose_name_plural': 'Результаты прохождения тестов'},
        ),
    ]
