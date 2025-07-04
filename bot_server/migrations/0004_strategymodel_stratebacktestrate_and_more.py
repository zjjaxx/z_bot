# Generated by Django 5.1.6 on 2025-06-29 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bot_server", "0003_remove_strategymodel_strateoperatetime"),
    ]

    operations = [
        migrations.AddField(
            model_name="strategymodel",
            name="strateBackTestRate",
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name="strategymodel",
            name="strateLossCount",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="strategymodel",
            name="strateWinCount",
            field=models.IntegerField(default=0),
        ),
    ]
