# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-02 14:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('octapp', '0004_auto_20170425_1657'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resultscale',
            name='name',
            field=models.CharField(max_length=70, unique=True, verbose_name='Наименование шкалы'),
        ),
    ]