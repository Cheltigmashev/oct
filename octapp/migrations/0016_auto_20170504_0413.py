# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-03 21:13
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('octapp', '0015_auto_20170504_0336'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='questionoftest',
            options={'ordering': ['test'], 'verbose_name': 'Вопрос теста', 'verbose_name_plural': 'Вопросы теста'},
        ),
    ]
