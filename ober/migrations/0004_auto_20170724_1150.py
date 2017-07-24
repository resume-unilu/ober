# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-24 11:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ober', '0003_story_doi'),
    ]

    operations = [
        migrations.CreateModel(
            name='Publisher',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('rss_url', models.URLField(max_length=256, unique=True)),
                ('status', models.CharField(choices=[(b'crawling', b'crawling'), (b'ready', b'ready')], db_index=True, default=b'ready', max_length=10)),
                ('date_last_crawled', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AddField(
            model_name='story',
            name='publisher',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='stories', to='ober.Publisher'),
        ),
    ]
