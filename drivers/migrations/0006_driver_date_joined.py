# Generated by Django 4.0.4 on 2024-05-19 14:23

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drivers', '0005_driver_driver_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='driver',
            name='date_joined',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]
