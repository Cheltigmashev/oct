# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-02 17:53
from __future__ import unicode_literals

import ckeditor.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('octapp', '0005_auto_20170502_2129'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClosedQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('only_one_right', models.BooleanField(default=True, verbose_name='Только один вариант ответа — правильный')),
                ('question_content', ckeditor.fields.RichTextField(help_text='Используйте сервисы хранения изображений, если требуется добавить картинку.', verbose_name='Содержимое (наполнение, контент) вопроса.')),
                ('question_index_number', models.IntegerField(verbose_name='Порядковый номер вопроса в тесте')),
                ('correct_option_numbers', models.CharField(max_length=55, verbose_name='Номера одного или нескольких правильных вариантов через запятую и без пробелов')),
                ('test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='closed_questions', to='octapp.Test', verbose_name='Тест, к которому относится вопрос')),
            ],
            options={
                'ordering': ['test'],
                'verbose_name': 'Вопрос закрытого типа',
                'verbose_name_plural': 'Вопросы закрытого типа',
            },
        ),
        migrations.CreateModel(
            name='ComparisonQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_content', ckeditor.fields.RichTextField(verbose_name='Содержимое (наполнение, контент) вопроса')),
                ('correct_sequence', models.CharField(help_text='Номера элементов последовательности второго ряда, разделенные запятыми без пробелов.', max_length=55, verbose_name='Правильная последовательность элементов второго (правого) ряда (столбца)')),
                ('question_index_number', models.IntegerField(verbose_name='Порядковый номер вопроса в тесте')),
                ('test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comparison_questions', to='octapp.Test', verbose_name='Тест, к которому относится вопрос')),
            ],
            options={
                'ordering': ['test'],
                'verbose_name': 'Вопрос на сопоставление',
                'verbose_name_plural': 'Вопросы на сопоставление',
            },
        ),
        migrations.CreateModel(
            name='OpenQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_content_before_blank', ckeditor.fields.RichTextField(verbose_name='Содержимое (наполнение, контент) вопроса перед пропуском')),
                ('question_content_after_blank', ckeditor.fields.RichTextField(blank=True, null=True, verbose_name='Содержимое (наполнение, контент) вопроса после пропуска (может отсутствовать)')),
                ('correct_option', models.CharField(max_length=120, verbose_name='Текст правильного ответа')),
                ('question_index_number', models.IntegerField(verbose_name='Порядковый номер вопроса в тесте')),
                ('test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='open_questions', to='octapp.Test', verbose_name='Тест, к которому относится вопрос')),
            ],
            options={
                'ordering': ['test'],
                'verbose_name': 'Вопрос открытого типа',
                'verbose_name_plural': 'Вопросы открытого типа',
            },
        ),
        migrations.CreateModel(
            name='SequenceQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_content', ckeditor.fields.RichTextField(verbose_name='Содержимое (наполнение, контент) вопроса')),
                ('correct_sequence', models.CharField(help_text='Номера элементов последовательности, разделенные запятыми без пробелов.', max_length=55, verbose_name='Правильная последовательность')),
                ('question_index_number', models.IntegerField(verbose_name='Порядковый номер вопроса в тесте')),
                ('test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sequence_questions', to='octapp.Test', verbose_name='Тест, к которому относится вопрос')),
            ],
            options={
                'ordering': ['test'],
                'verbose_name': 'Вопрос на определение последовательности (порядка) элементов',
                'verbose_name_plural': 'Вопросы на определение последовательности (порядка) элементов',
            },
        ),
        migrations.CreateModel(
            name='SequenceQuestionElement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('element_index_number', models.IntegerField(verbose_name='Порядковый номер элемента последовательности')),
                ('sequence_question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sequence_elements', to='octapp.SequenceQuestion', verbose_name='Вопрос на определение последовательности, к которому относится элемент')),
            ],
            options={
                'ordering': ['element_index_number'],
                'verbose_name': 'Элемент для вопроса на определение последовательности',
                'verbose_name_plural': 'Элементы для вопроса на определение последовательности',
            },
        ),
        migrations.AlterField(
            model_name='comment',
            name='content',
            field=ckeditor.fields.RichTextField(verbose_name='Содержимое (наполнение, контент) комментария'),
        ),
    ]
