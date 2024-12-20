from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.timezone import now


class Client(models.Model):
    client_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    gstn = models.CharField(max_length=15, default='URP')
    place_of_supply = models.CharField(max_length=15, null=False, default='Kerala')
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=255)
    last_updated_on = models.DateTimeField(auto_now=True)
    last_updated_by = models.CharField(max_length=255)

class CustomUser(AbstractUser):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    USERNAME_FIELD = 'username'  # Change this if you use a different field for login

    def __str__(self):
        return self.username

class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=255, null=False)
    HSN_code = models.CharField(max_length=50, null=False)
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=False)
    discount_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, default=0)
    unit = models.CharField(max_length=50, null=False)
    category = models.CharField(max_length=100, blank=True, null=True)
    brand = models.CharField(max_length=100, blank=True, null=True)
    price_after_tax = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    price_before_tax = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0.00)
    sales_rank = models.IntegerField(blank=True, null=True)
    created_on = models.DateTimeField(default=timezone.now)
    created_by = models.CharField(max_length=255)
    last_updated_on = models.DateTimeField(default=timezone.now)
    last_updated_by = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'Product'
        ordering = ['product_id']

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=False)
    address = models.TextField(null=True)
    phone = models.CharField(max_length=15, null=False)
    email_id = models.EmailField(null=True)
    category = models.CharField(max_length=50, null=False)
    GSTIN = models.CharField(max_length=15, null=True)
    password = models.CharField(max_length=128, null=True)
    otp = models.CharField(max_length=6, null=True)
    sales_rank = models.IntegerField(null=True)
    created_on = models.DateTimeField(default=timezone.now)
    created_by = models.CharField(max_length=50)
    last_updated_on = models.DateTimeField(default=timezone.now)
    last_updated_by = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'Customer'
        ordering = ['customer_id']

# Customer_Bill Model
class CustomerBill(models.Model):
    bill_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    client = models.ForeignKey('Client', on_delete=models.CASCADE)
    invoice_no = models.CharField(max_length=50, unique=True)
    invoice_date = models.DateField(default=None)
    place_of_supply = models.CharField(max_length=255)
    total_amount_before_tax = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=[
        ('Estimate', 'Estimate'),
        ('Invoice', 'Invoice'),
        ('Advance paid', 'Advance paid'),
        ('Partially paid', 'Partially paid'),
        ('Completely paid', 'Completely paid'),
        ('Cancelled', 'Cancelled')
    ])
    is_rcm = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=255)
    last_updated_on = models.DateTimeField(auto_now=True)
    last_updated_by = models.CharField(max_length=255)

# Bill_Items Model
class BillItem(models.Model):
    bill_item_id = models.AutoField(primary_key=True)
    bill = models.ForeignKey(CustomerBill, on_delete=models.CASCADE)
    client = models.ForeignKey('Client', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    qty = models.PositiveIntegerField()
    unit = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2)
    taxable_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=255)
    last_updated_on = models.DateTimeField(auto_now=True)
    last_updated_by = models.CharField(max_length=255)

# Bill_Tax_Splits Model
class BillTaxSplit(models.Model):
    bts_id = models.AutoField(primary_key=True)
    bill = models.ForeignKey(CustomerBill, on_delete=models.CASCADE)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2)
    SGST = models.DecimalField(max_digits=10, decimal_places=2)
    CGST = models.DecimalField(max_digits=10, decimal_places=2)
    IGST = models.DecimalField(max_digits=10, decimal_places=2)
    CESS = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=255)
    last_updated_on = models.DateTimeField(auto_now=True)
    last_updated_by = models.CharField(max_length=255)

class Vendor(models.Model):
    vendor_id = models.AutoField(primary_key=True)
    client = models.ForeignKey('Client', on_delete=models.CASCADE, related_name="vendors")
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=15)
    email_id = models.EmailField(null=True, blank=True)
    place_of_supply = models.CharField(max_length=255)
    GSTIN = models.CharField(max_length=15, default="NRP")
    is_inactive = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=255)
    last_updated_on = models.DateTimeField(auto_now=True)
    last_updated_by = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'Vendor'
        ordering = ['vendor_id']