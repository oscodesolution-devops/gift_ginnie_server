# Generated by Django 5.1.4 on 2025-01-13 10:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0003_remove_productcategory_image_link_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="images",
            field=models.ManyToManyField(
                related_name="products", to="products.productimage"
            ),
        ),
        migrations.AlterField(
            model_name="productimage",
            name="product",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="products.product",
            ),
        ),
    ]
