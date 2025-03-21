# Generated by Django 5.1.4 on 2025-03-21 20:43

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('products', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='favouriteproduct',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favourite_products', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='giftforyou',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gifts', to='products.product'),
        ),
        migrations.AddField(
            model_name='favouriteproduct',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favourites', to='products.product'),
        ),
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='products.productcategory'),
        ),
        migrations.AddField(
            model_name='giftforyou',
            name='product_category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gifts_for_you', to='products.productcategory'),
        ),
        migrations.AddField(
            model_name='productimage',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='images', to='products.product'),
        ),
    ]
