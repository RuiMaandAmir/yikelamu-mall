# Generated by Django 5.0.1 on 2025-01-21 03:18

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="user",
            options={
                "ordering": ["-date_joined"],
                "verbose_name": "用户",
                "verbose_name_plural": "用户管理",
            },
        ),
    ]
