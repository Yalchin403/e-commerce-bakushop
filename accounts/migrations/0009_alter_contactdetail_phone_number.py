# Generated by Django 4.1.2 on 2023-01-08 21:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0008_rename_contact_contactdetail"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contactdetail",
            name="phone_number",
            field=models.CharField(max_length=20),
        ),
    ]
