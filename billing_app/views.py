from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from django.contrib.auth import authenticate
from django.db import transaction
from .serializers import CustomUserSerializer, ClientSerializer
from .permissions import IsSuperAdminUser

# Login View
class CustomUserLoginView(APIView):
    permission_classes = [AllowAny]  # Allow access to all users

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        print("Received Username:", username)  # Debugging
        print("Received Password:", password)  # Debugging

        # Authenticate user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            client_id = user.client_id

            # Generate tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            # Set cookies
            response = Response({"message": "Login successful"}, status=status.HTTP_200_OK)
            response.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                secure=True,
                samesite='Lax'
            )
            response.set_cookie(
                key='refresh_token',
                value=str(refresh),
                httponly=True,
                secure=True,
                samesite='Lax'
            )
            response.set_cookie(
                key='client_id',
                value=client_id,
                httponly=True,
                secure=True,
                samesite='Lax'
            )

            return response
        else:
            print("Authentication failed")  # Debugging
            return Response({"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

# Token Refresh View
class CustomTokenRefreshView(APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({"message": "Refresh token missing"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Validate refresh token
            refresh = RefreshToken(refresh_token)
            new_access_token = str(refresh.access_token)

            # Set new access token in cookie
            response = Response({"message": "Token refreshed"}, status=status.HTTP_200_OK)
            response.set_cookie(
                key='access_token',
                value=new_access_token,
                httponly=True,
                secure=True,
                samesite='Lax'
            )
            return response

        except InvalidToken:
            return Response({"message": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)

# Logout View
class CustomUserLogoutView(APIView):
    def post(self, request):
        response = Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        response.delete_cookie('client_id')
        return response

class CreateUserView(APIView):
    permission_classes = [IsSuperAdminUser]  # Restrict access to superusers or "superadmin"
    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User created successfully", "user_id": user.id}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CreateClientView(APIView):
    permission_classes = [IsSuperAdminUser]  # Restrict access to superusers or "superadmin"
    def post(self, request):
        serializer = ClientSerializer(data=request.data)
        if serializer.is_valid():
            client = serializer.save()
            return Response({"message": "Client created successfully", "client_id": client.client_id}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "This is a protected view. Access granted!"})