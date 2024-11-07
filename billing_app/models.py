from django.contrib.auth.models import AbstractUser
from django.db import models

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
