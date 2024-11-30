from rest_framework import serializers
from .models import CustomUser, Client, Product, Customer, CustomerBill, BillItem, BillTaxSplit
from django.contrib.auth.hashers import make_password

class CustomUserSerializer(serializers.ModelSerializer):
    client_id = serializers.IntegerField(write_only=True)  # Use client_id instead of client object

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'client_id', 'phone', 'address', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        client_id = validated_data.pop('client_id')
        try:
            client = Client.objects.get(client_id=client_id)
        except Client.DoesNotExist:
            raise serializers.ValidationError({"client_id": "Invalid client ID"})

        # Hash the password
        validated_data['password'] = make_password(validated_data['password'])
        user = CustomUser.objects.create(client=client, **validated_data)
        return user


class ClientSerializer(serializers.ModelSerializer):
    client_id = serializers.IntegerField(required=True)  # Allow manual input for client_id

    class Meta:
        model = Client
        fields = ['client_id', 'name', 'address', 'phone', 'email', 'gstn', 'place_of_supply' 'created_by', 'last_updated_by']

    def create(self, validated_data):
        # Check if the client_id is already taken
        if Client.objects.filter(client_id=validated_data['client_id']).exists():
            raise serializers.ValidationError({"client_id": "This client ID is already in use."})

        return Client.objects.create(**validated_data)

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'product_id', 'client', 'name', 'HSN_code', 'tax_percentage', 'discount_rate',
            'unit', 'category', 'brand', 'price_after_tax', 'price_before_tax', 'sales_rank',
            'created_on', 'created_by', 'last_updated_on', 'last_updated_by'
        ]

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            'customer_id', 'client', 'name', 'address', 'phone', 'email_id', 'category',
            'GSTIN', 'password', 'otp', 'sales_rank', 'created_on', 'created_by',
            'last_updated_on', 'last_updated_by'
        ]
        extra_kwargs = {
            'password': {'write_only': True},  # Hide password field in responses
            'otp': {'write_only': True}        # Hide OTP field in responses
        }

# Customer_Bill Serializer
class CustomerBillSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerBill
        fields = '__all__'

# Bill_Items Serializer
class BillItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillItem
        fields = '__all__'

# Bill_Tax_Splits Serializer
class BillTaxSplitSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillTaxSplit
        fields = '__all__'
