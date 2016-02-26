# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_app', '0002_auto_20151113_1200'),
    ]

    operations = [
        migrations.RenameField(
            model_name='text',
            old_name='article_name',
            new_name='article_object',
        ),
    ]
