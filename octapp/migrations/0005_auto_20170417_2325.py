# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-17 16:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('octapp', '0004_auto_20170417_2217'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tag',
            name='test',
        ),
        migrations.AddField(
            model_name='test',
            name='tag',
            field=models.ManyToManyField(to='octapp.Tag'),
        ),
    ]
