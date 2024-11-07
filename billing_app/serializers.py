from rest_framework import serializers
from .models import CustomUser, Client
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
        fields = ['client_id', 'name', 'address', 'phone', 'email', 'created_by', 'last_updated_by']

    def create(self, validated_data):
        # Check if the client_id is already taken
        if Client.objects.filter(client_id=validated_data['client_id']).exists():
            raise serializers.ValidationError({"client_id": "This client ID is already in use."})

        return Client.objects.create(**validated_data)