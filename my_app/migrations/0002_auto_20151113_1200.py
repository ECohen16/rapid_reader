# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Text',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('article_text', models.CharField(max_length=50000)),
            ],
        ),
        migrations.AddField(
            model_name='article',
            name='url_address',
            field=models.CharField(null=True, max_length=140, blank=True),
        ),
        migrations.AddField(
            model_name='text',
            name='article_name',
            field=models.ForeignKey(to='my_app.Article'),
        ),
    ]
