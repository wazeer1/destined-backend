# Generated by Django 5.1.1 on 2024-09-19 06:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_user_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='enc_password',
            field=models.TextField(blank=True, null=True),
        ),
    ]
