# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2019-10-10 07:59
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Arya', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='host',
            table='tb_host',
        ),
        migrations.AlterModelTable(
            name='hostgroup',
            table='tb_hostgroup',
        ),
    ]
