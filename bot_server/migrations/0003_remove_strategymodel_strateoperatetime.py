# Generated by Django 5.1.6 on 2025-06-28 21:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("bot_server", "0002_alter_strategymodel_strateoperatetime"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="strategymodel",
            name="strateOperateTime",
        ),
    ]
