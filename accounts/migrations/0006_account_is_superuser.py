# Generated by Django 4.0.6 on 2022-09-10 20:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0005_remove_account_is_superuser"),
    ]

    operations = [
        migrations.AddField(
            model_name="account",
            name="is_superuser",
            field=models.BooleanField(default=False),
        ),
    ]
