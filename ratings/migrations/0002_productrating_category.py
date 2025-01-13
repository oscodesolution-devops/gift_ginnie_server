# Generated by Django 5.1.4 on 2025-01-08 13:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0002_carouselitem"),
        ("ratings", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="productrating",
            name="category",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="products.productcategory",
            ),
            preserve_default=False,
        ),
    ]
