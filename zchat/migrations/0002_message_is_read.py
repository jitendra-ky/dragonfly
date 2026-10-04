from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("zchat", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="message",
            name="is_read",
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name="message",
            name="is_read",
            field=models.BooleanField(default=False),
        ),
    ]
