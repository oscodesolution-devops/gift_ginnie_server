# Generated by Django 5.1.4 on 2025-01-15 10:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_couponusage'),
    ]

    operations = [
        migrations.AddField(
            model_name='coupon',
            name='max_usage',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='coupon',
            name='max_usage_per_user',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
