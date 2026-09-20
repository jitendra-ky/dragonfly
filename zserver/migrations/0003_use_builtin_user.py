from typing import Any

from django.db import migrations, models


def copy_users_to_auth(apps: Any, schema_editor: Any) -> None:  # noqa: ANN401
    old_user = apps.get_model("zserver", "User")
    old_unverified_user = apps.get_model("zserver", "UnverifiedUser")
    auth_user = apps.get_model("auth", "User")
    database = schema_editor.connection.alias

    for user in old_user.objects.using(database).all():
        auth_user.objects.using(database).update_or_create(
            id=user.id,
            defaults={
                "username": user.email,
                "first_name": user.contact,
                "email": user.email,
                "password": user.password,
                "is_active": user.is_active,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
                "last_login": user.last_login,
            },
        )

    with schema_editor.connection.cursor() as cursor:
        for user in old_unverified_user.objects.using(database).all():
            migrated_user = auth_user.objects.using(database).create(
                username=user.email,
                first_name=user.contact,
                email=user.email,
                password=user.password,
                is_active=False,
                is_staff=False,
                is_superuser=False,
            )
            cursor.execute(
                "UPDATE zserver_verifyuserotp SET user_id = %s WHERE user_id = %s",
                [migrated_user.id, user.id],
            )


class Migration(migrations.Migration):

    dependencies = [
        ("zserver", "0002_delete_session"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.RunPython(copy_users_to_auth, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="verifyuserotp",
            name="user",
            field=models.ForeignKey(
                on_delete=models.CASCADE,
                to="auth.user",
            ),
        ),
        migrations.DeleteModel(
            name="UnverifiedUser",
        ),
        migrations.DeleteModel(
            name="User",
        ),
    ]
