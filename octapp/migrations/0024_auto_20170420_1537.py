# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-20 08:37
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('octapp', '0023_auto_20170420_1441'),
    ]

    operations = [
        migrations.AlterField(
            model_name='test_rate',
            name='reviewer',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='rates', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь, к которому относится данная пользовательская оценка (рейтинг)'),
            preserve_default=False,
        ),
    ]
