# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-17 06:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ober', '0008_publisher_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publisher',
            name='status',
            field=models.CharField(choices=[(b'preflight', b'preflight'), (b'crawling', b'crawling'), (b'ready', b'ready'), (b'error', b'error')], db_index=True, default=b'ready', max_length=10),
        ),
        migrations.AlterField(
            model_name='story',
            name='short_url',
            field=models.CharField(db_index=True, max_length=22),
        ),
        migrations.AlterUniqueTogether(
            name='story',
            unique_together=set([('publisher', 'short_url')]),
        ),
    ]