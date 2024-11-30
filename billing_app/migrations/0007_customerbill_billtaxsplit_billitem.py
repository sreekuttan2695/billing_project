# Generated by Django 5.1.3 on 2024-11-30 18:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing_app', '0006_client_gstn_client_place_of_supply'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerBill',
            fields=[
                ('bill_id', models.AutoField(primary_key=True, serialize=False)),
                ('invoice_no', models.CharField(max_length=50, unique=True)),
                ('invoice_date', models.DateField(default=None)),
                ('place_of_supply', models.CharField(max_length=255)),
                ('total_amount_before_tax', models.DecimalField(decimal_places=2, max_digits=10)),
                ('discount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(choices=[('Estimate', 'Estimate'), ('Invoice', 'Invoice'), ('Advance paid', 'Advance paid'), ('Partially paid', 'Partially paid'), ('Completely paid', 'Completely paid'), ('Cancelled', 'Cancelled')], max_length=50)),
                ('is_rcm', models.BooleanField(default=False)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.CharField(max_length=255)),
                ('last_updated_on', models.DateTimeField(auto_now=True)),
                ('last_updated_by', models.CharField(max_length=255)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing_app.client')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing_app.customer')),
            ],
        ),
        migrations.CreateModel(
            name='BillTaxSplit',
            fields=[
                ('bts_id', models.AutoField(primary_key=True, serialize=False)),
                ('tax_rate', models.DecimalField(decimal_places=2, max_digits=5)),
                ('SGST', models.DecimalField(decimal_places=2, max_digits=10)),
                ('CGST', models.DecimalField(decimal_places=2, max_digits=10)),
                ('IGST', models.DecimalField(decimal_places=2, max_digits=10)),
                ('CESS', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.CharField(max_length=255)),
                ('last_updated_on', models.DateTimeField(auto_now=True)),
                ('last_updated_by', models.CharField(max_length=255)),
                ('bill', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing_app.customerbill')),
            ],
        ),
        migrations.CreateModel(
            name='BillItem',
            fields=[
                ('bill_item_id', models.AutoField(primary_key=True, serialize=False)),
                ('qty', models.PositiveIntegerField()),
                ('unit', models.CharField(max_length=50)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('discount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('tax_rate', models.DecimalField(decimal_places=2, max_digits=5)),
                ('taxable_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.CharField(max_length=255)),
                ('last_updated_on', models.DateTimeField(auto_now=True)),
                ('last_updated_by', models.CharField(max_length=255)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing_app.client')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing_app.product')),
                ('bill', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing_app.customerbill')),
            ],
        ),
    ]
