# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-20 17:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('octapp', '0026_auto_20170420_2349'),
    ]

    operations = [
        migrations.AlterField(
            model_name='test',
            name='time_restricting',
            field=models.TimeField(blank=True, null=True, verbose_name='Ограничение времени прохождения теста в минутах'),
        ),
    ]
