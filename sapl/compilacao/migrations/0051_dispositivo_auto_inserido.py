# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-09-12 16:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compilacao', '0050_auto_20160503_0926'),
    ]

    operations = [
        migrations.AddField(
            model_name='dispositivo',
            name='auto_inserido',
            field=models.BooleanField(choices=[(True, 'Sim'), (False, 'Não')], default=False, verbose_name='Auto Inserido'),
        ),
    ]
