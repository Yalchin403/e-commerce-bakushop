# Generated by Django 4.1.2 on 2023-01-22 20:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0009_alter_contactdetail_phone_number"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="ContactDetail",
            new_name="AccountDetail",
        ),
    ]
