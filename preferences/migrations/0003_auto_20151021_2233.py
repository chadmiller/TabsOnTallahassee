# -*- coding: utf-8 -*-
# Generated by Django 1.9a1 on 2015-10-21 22:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('preferences', '0002_auto_20151021_0154'),
    ]

    operations = [
        migrations.AlterField(
            model_name='preferences',
            name='address',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]