# Generated by Django 4.0.4 on 2024-05-18 13:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drivers', '0003_remove_driver_car_number_driver_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='driver',
            name='status',
        ),
    ]