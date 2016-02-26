# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_app', '0006_readinglist'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArticleSource',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('source_name', models.CharField(max_length=30)),
            ],
        ),
    ]
