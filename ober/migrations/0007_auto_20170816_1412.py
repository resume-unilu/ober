# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-16 14:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ober', '0006_auto_20170724_1154'),
    ]

    operations = [
        migrations.RenameField(
            model_name='publisher',
            old_name='url',
            new_name='endpoint',
        ),
        migrations.RemoveField(
            model_name='publisher',
            name='rss_url',
        ),
        migrations.AddField(
            model_name='publisher',
            name='date_last_updated',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='publisher',
            name='status',
            field=models.CharField(choices=[(b'preflight', b'preflight'), (b'crawling', b'crawling'), (b'ready', b'ready')], db_index=True, default=b'ready', max_length=10),
        ),
    ]
