# Generated by Django 5.1.6 on 2025-02-18 23:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bot_server", "0005_alter_strategymodel_strateoperate"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="strategymodel",
            name="pnl_desc",
        ),
        migrations.AlterField(
            model_name="strategymodel",
            name="strateOperate",
            field=models.IntegerField(
                choices=[
                    (1, "重仓买入"),
                    (3, "轻仓买入"),
                    (-1, "卖出"),
                    (2, "中等仓位"),
                ]
            ),
        ),
    ]
