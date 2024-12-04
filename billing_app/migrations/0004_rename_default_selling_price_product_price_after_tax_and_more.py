# Generated by Django 5.1.3 on 2024-11-17 14:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing_app', '0003_customer'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='default_selling_price',
            new_name='price_after_tax',
        ),
        migrations.AddField(
            model_name='product',
            name='discount_rate',
            field=models.DecimalField(decimal_places=2, max_digits=5, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='price_before_tax',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]