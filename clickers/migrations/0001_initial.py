# Generated by Django 4.1.4 on 2023-01-06 17:54

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Clicker",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("block", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("ipaddress", models.GenericIPAddressField(db_index=True)),
                ("useragent", models.CharField(max_length=256)),
            ],
            options={
                "db_table": "clickers",
            },
        ),
    ]