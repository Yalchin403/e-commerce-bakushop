# Generated by Django 4.0.6 on 2022-08-25 20:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_account_activation_key_account_otp'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='is_superuser',
            field=models.BooleanField(default=False),
        ),
    ]
