# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-03 14:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('octapp', '0008_auto_20170503_0203'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuestionOfTest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_index_number', models.IntegerField(verbose_name='Порядковый номер вопроса в тесте')),
                ('type_of_question', models.CharField(choices=[('CQ', 'закрытый'), ('OQ', 'открытый'), ('SQ', 'последовательность'), ('CQ', 'сопоставление')], max_length=2, unique=True, verbose_name='Тип теста, чтобы знать, к какому типу вопроса обращаться через связь')),
                ('test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions_of_test', to='octapp.Test', verbose_name='Тест, к которому относится вопрос')),
            ],
            options={
                'verbose_name': 'Вопрос (как пункт) теста',
                'ordering': ['test'],
                'verbose_name_plural': 'Вопросы (как пункт) теста',
            },
        ),
        migrations.AlterModelOptions(
            name='closedquestion',
            options={'ordering': ['question_of_test'], 'verbose_name': 'Вопрос закрытого типа', 'verbose_name_plural': 'Вопросы закрытого типа'},
        ),
        migrations.AlterModelOptions(
            name='closedquestionoption',
            options={'ordering': ['question'], 'verbose_name': 'Вариант ответа на вопрос закрытого типа', 'verbose_name_plural': 'Варианты ответа на вопрос закрытого типа'},
        ),
        migrations.AlterModelOptions(
            name='comparisonquestion',
            options={'ordering': ['question_of_test'], 'verbose_name': 'Вопрос на сопоставление', 'verbose_name_plural': 'Вопросы на сопоставление'},
        ),
        migrations.AlterModelOptions(
            name='openquestion',
            options={'ordering': ['question_of_test'], 'verbose_name': 'Вопрос открытого типа', 'verbose_name_plural': 'Вопросы открытого типа'},
        ),
        migrations.AlterModelOptions(
            name='sequencequestion',
            options={'ordering': ['question_of_test'], 'verbose_name': 'Вопрос на определение последовательности (порядка) элементов', 'verbose_name_plural': 'Вопросы на определение последовательности (порядка) элементов'},
        ),
        migrations.AlterModelOptions(
            name='sequencequestionelement',
            options={'ordering': ['question'], 'verbose_name': 'Элемент для вопроса на определение последовательности', 'verbose_name_plural': 'Элементы для вопроса на определение последовательности'},
        ),
        migrations.RemoveField(
            model_name='closedquestion',
            name='question_index_number',
        ),
        migrations.RemoveField(
            model_name='closedquestion',
            name='test',
        ),
        migrations.RemoveField(
            model_name='comparisonquestion',
            name='question_index_number',
        ),
        migrations.RemoveField(
            model_name='comparisonquestion',
            name='test',
        ),
        migrations.RemoveField(
            model_name='openquestion',
            name='question_index_number',
        ),
        migrations.RemoveField(
            model_name='openquestion',
            name='test',
        ),
        migrations.RemoveField(
            model_name='sequencequestion',
            name='question_index_number',
        ),
        migrations.RemoveField(
            model_name='sequencequestion',
            name='test',
        ),
        migrations.AlterField(
            model_name='closedquestionoption',
            name='option_number',
            field=models.IntegerField(verbose_name='Порядковый номер варианта ответа на вопрос закр. типа'),
        ),
        migrations.AlterField(
            model_name='sequencequestion',
            name='correct_sequence',
            field=models.CharField(help_text='Номера элементов последовательности, разделенные запятыми без пробелов.', max_length=70, verbose_name='Правильная последовательность'),
        ),
        migrations.AddField(
            model_name='closedquestion',
            name='question_of_test',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='closed_question', to='octapp.QuestionOfTest', verbose_name='Нумерованный элемент (пункт) списка вопросов'),
        ),
        migrations.AddField(
            model_name='comparisonquestion',
            name='question_of_test',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comparison_question', to='octapp.QuestionOfTest', verbose_name='Нумерованный элемент (пункт) списка вопросов'),
        ),
        migrations.AddField(
            model_name='openquestion',
            name='question_of_test',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='open_question', to='octapp.QuestionOfTest', verbose_name='Нумерованный элемент (пункт) списка вопросов'),
        ),
        migrations.AddField(
            model_name='sequencequestion',
            name='question_of_test',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sequence_question', to='octapp.QuestionOfTest', verbose_name='Нумерованный элемент (пункт) списка вопросов'),
        ),
    ]
