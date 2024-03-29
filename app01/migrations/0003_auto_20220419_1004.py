# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2022-04-19 10:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0002_remove_usersite_site_style'),
    ]

    operations = [
        migrations.CreateModel(
            name='Usersite2Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.RemoveField(
            model_name='tag',
            name='usersite',
        ),
        migrations.RemoveField(
            model_name='userinfo',
            name='phone',
        ),
        migrations.AddField(
            model_name='usersite2tag',
            name='tag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app01.Tag'),
        ),
        migrations.AddField(
            model_name='usersite2tag',
            name='usersite',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app01.Usersite'),
        ),
        migrations.AddField(
            model_name='usersite',
            name='tags',
            field=models.ManyToManyField(through='app01.Usersite2Tag', to='app01.Tag'),
        ),
    ]
