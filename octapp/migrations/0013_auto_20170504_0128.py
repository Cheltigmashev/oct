# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-03 18:28
from __future__ import unicode_literals

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('octapp', '0012_auto_20170504_0122'),
    ]

    operations = [
        migrations.AlterField(
            model_name='closedquestion',
            name='question_content',
            field=ckeditor.fields.RichTextField(default='', help_text='Используйте сервисы хранения изображений, если требуется добавить картинку.', verbose_name='Содержимое (контент) вопроса'),
        ),
    ]
