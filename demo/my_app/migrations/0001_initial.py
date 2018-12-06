# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-11-30 06:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='id')),
                ('nr', models.CharField(db_index=True, max_length=300, unique=True, verbose_name='customer nr')),
                ('name', models.CharField(db_index=True, max_length=300, verbose_name='name')),
                ('area', models.CharField(blank=True, db_index=True, max_length=300, null=True, verbose_name='area')),
                ('address', models.CharField(blank=True, db_index=True, max_length=300, null=True, verbose_name='address')),
            ],
            options={
                'db_table': 'customer',
                'permissions': (('just test', '测试一下'),),
            },
        ),
    ]
