# Generated by Django 5.1.4 on 2025-01-22 07:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0013_remove_couponusage_title_coupon_description_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='couponusage',
            unique_together=set(),
        ),
    ]
