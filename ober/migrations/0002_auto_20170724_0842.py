# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-24 08:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('ober', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='story',
            options={'ordering': ('-date_last_modified',), 'verbose_name_plural': 'stories'},
        ),
        migrations.AddField(
            model_name='story',
            name='date',
            field=models.DateTimeField(blank=True, db_index=True, null=True),
        ),
        migrations.AddField(
            model_name='story',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='story',
            name='date_last_modified',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
