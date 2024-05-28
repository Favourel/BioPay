# Generated by Django 4.0.4 on 2024-05-25 14:12

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('drivers', '0007_ride_fare'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ride',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True),
        ),
    ]
