# Generated by Django 4.0.4 on 2024-05-15 16:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='account_balance',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
