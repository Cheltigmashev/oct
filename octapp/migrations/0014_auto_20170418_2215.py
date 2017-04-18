# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-18 15:15
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('octapp', '0013_auto_20170418_2145'),
    ]

    operations = [
        migrations.AlterField(
            model_name='test',
            name='author',
            field=models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tests', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь, загрузивший тест'),
        ),
    ]