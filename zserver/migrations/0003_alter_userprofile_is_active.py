# Generated by Django 5.1.5 on 2025-02-07 07:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("zserver", "0002_session"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userprofile",
            name="is_active",
            field=models.BooleanField(default=False),
        ),
    ]
