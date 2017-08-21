# -*- coding: utf-8 -*-
# Add pg_trigram extension. This requires PostgresQL user to be superuser
# `ALTER USER resume WITH SUPERUSER;` 
# and DO NOT FORGET TO user role when the migration is done.
# `ALTER USER myuser WITH NOSUPERUSER`
from __future__ import unicode_literals

from django.db import migrations

from django.contrib.postgres.operations import TrigramExtension, UnaccentExtension


class Migration(migrations.Migration):

    dependencies = [
        ('ober', '0009_auto_20170817_0646'),
    ]

    operations = [
        TrigramExtension(),
        UnaccentExtension()
    ]
