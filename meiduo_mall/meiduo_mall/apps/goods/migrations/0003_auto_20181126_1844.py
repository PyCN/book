# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-11-26 10:44
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0002_auto_20181120_1900'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='goodschannel',
            options={'ordering': ['group_id', 'sequence'], 'verbose_name': '商品频道', 'verbose_name_plural': '商品频道'},
        ),
    ]