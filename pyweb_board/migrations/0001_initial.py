# Generated by Django 4.2.5 on 2023-09-14 06:52

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Board',
            fields=[
                ('idx', models.AutoField(primary_key=True, serialize=False)),
                ('writer', models.CharField(max_length=50)),
                ('title', models.CharField(max_length=120)),
                ('hit', models.IntegerField(default=0)),
                ('content', models.TextField()),
                ('post_date', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('filename', models.CharField(blank=True, default='', max_length=500, null=True)),
                ('filesize', models.IntegerField(default=0)),
                ('down', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('idx', models.AutoField(primary_key=True, serialize=False)),
                ('board_idx', models.IntegerField()),
                ('writer', models.CharField(max_length=50)),
                ('content', models.TextField()),
                ('post_date', models.DateTimeField(blank=True, default=datetime.datetime.now)),
            ],
        ),
    ]
