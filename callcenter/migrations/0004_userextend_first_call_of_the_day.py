# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-25 00:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('callcenter', '0003_auto_20170225_0044'),
    ]

    operations = [
        migrations.AddField(
            model_name='userextend',
            name='first_call_of_the_day',
            field=models.DateTimeField(auto_now=True),
        ),
    ]