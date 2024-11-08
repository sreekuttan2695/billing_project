from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class Client(models.Model):
    client_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
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
    unit = models.CharField(max_length=50, null=False)
    category = models.CharField(max_length=100, blank=True, null=True)
    brand = models.CharField(max_length=100, blank=True, null=True)
    default_selling_price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
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
