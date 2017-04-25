# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-25 07:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('octapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40, unique=True, verbose_name='Наименование тега')),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Тег',
                'verbose_name_plural': 'Теги',
            },
        ),
        migrations.AddField(
            model_name='test',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='tests', to='octapp.Tag', verbose_name='Тег или теги теста'),
        ),
    ]
