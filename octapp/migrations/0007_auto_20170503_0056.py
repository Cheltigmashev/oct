# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-02 17:56
from __future__ import unicode_literals

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('octapp', '0006_auto_20170503_0053'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='content',
            field=ckeditor.fields.RichTextField(help_text='Используйте сервисы хранения изображений, если требуется добавить картинку.', verbose_name='Содержимое (наполнение, контент) комментария'),
        ),
    ]
