# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-11 14:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('octapp', '0035_result'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comparisonquestion',
            name='correct_sequence',
            field=models.CharField(help_text='Перечислите здесь через запятую все правильные пары, например: 1-2, 2-1, 3-4, 4-3 (без точки)', max_length=55, verbose_name='Правильные пары элементов левого и правого столбцов (рядов) сопоставления'),
        ),
    ]
