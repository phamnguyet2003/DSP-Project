# Generated by Django 5.1.5 on 2025-02-02 14:51

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0004_payment_package"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="wallet",
            name="total",
        ),
    ]
