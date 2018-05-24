# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-05-24 11:49
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BalanceItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('group_id', models.CharField(max_length=255, verbose_name='groupId')),
                ('ordering', models.CharField(max_length=255, verbose_name='order')),
                ('count', models.IntegerField(default=0, verbose_name='count')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
