# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-06 15:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('octapp', '0024_auto_20170506_2212'),
    ]

    operations = [
        migrations.AlterField(
            model_name='openquestion',
            name='question_content_after_blank',
            field=models.TextField(blank=True, default='', null=True, verbose_name='Содержимое (контент) после пропуском (может отсутствовать)'),
        ),
    ]
