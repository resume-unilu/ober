# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-22 06:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ober', 'enable_psql_extensions'),
    ]

    operations = [
        migrations.AddField(
            model_name='story',
            name='search_text',
            field=models.TextField(blank=True, null=True),
        ),
    ]
