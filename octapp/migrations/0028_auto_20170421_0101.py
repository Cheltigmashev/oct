# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-20 18:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('octapp', '0027_auto_20170421_0045'),
    ]

    operations = [
        migrations.AlterField(
            model_name='test',
            name='time_restricting',
            field=models.IntegerField(blank=True, null=True, verbose_name='Ограничение времени прохождения теста в минутах'),
        ),
    ]
