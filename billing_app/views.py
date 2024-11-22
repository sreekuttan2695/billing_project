from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from django.contrib.auth import authenticate
from django.db import transaction
from .serializers import CustomUserSerializer, ClientSerializer, ProductSerializer
from .permissions import IsSuperAdminUser
from django.views import View
from django.http import JsonResponse
from django.db import connection
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

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

            response.set_cookie(
                key='username',
                value=username,
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
    permission_classes = [IsAuthenticated]
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

# /product end points starts here
@method_decorator(csrf_exempt, name='dispatch')
class ProductView(View):
    permission_classes = [IsAuthenticated]

    def get_client_id_from_cookie(self, request):
        client_id = request.client_id
        if not client_id:
            return JsonResponse({"error": "client_id is missing from cookies."}, status=400)
        return client_id

    def get_username_from_cookie(self, request):
        username = request.username
        if not username:
            return JsonResponse({"error": "username is missing from cookies."}, status=400)
        return username


    def get(self, request):
        client_id = self.get_client_id_from_cookie(request)
        # username = self.get_username_from_cookie(request)
        if isinstance(client_id, JsonResponse):  # If client_id retrieval failed, return the error response
            return client_id

        # Get query parameters for search and category filtering
        search_query = request.GET.get('search', '')
        selected_categories = request.GET.getlist('categories')  # Expects a list of categories

        # Base SQL query for fetching products
        sql_query = "SELECT product_id, name, HSN_code, tax_percentage, discount_rate, unit,category, brand,price_after_tax, price_before_tax, sales_rank FROM Product WHERE client_id = %s"
        params = [client_id]

        # Apply search filter if provided
        if search_query:
            sql_query += " AND name LIKE %s"
            params.append(f"%{search_query}%")

        # Apply category filter if any categories are selected
        if selected_categories:
            placeholders = ','.join(['%s'] * len(selected_categories))
            sql_query += f" AND category IN ({placeholders})"
            params.extend(selected_categories)

        # Order by product_id
        sql_query += " ORDER BY product_id"

        # Fetch products
        with connection.cursor() as cursor:
            cursor.execute(sql_query, params)
            products = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            product_list = [dict(zip(columns, product)) for product in products]

        # Fetch distinct categories for the sidebar filter
        with connection.cursor() as cursor:
            cursor.execute("SELECT DISTINCT category FROM Product WHERE client_id = %s", [client_id])
            categories = [row[0] for row in cursor.fetchall()]

        return JsonResponse({
            "products": product_list,
            "categories": categories
        }, status=200)

    def post(self, request):
        client_id = self.get_client_id_from_cookie(request)
        username = self.get_username_from_cookie(request)
        if isinstance(client_id, JsonResponse):
            return client_id

        data = json.loads(request.body)
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO Product (client_id, name, HSN_code, tax_percentage, discount_rate, unit, category, brand, 
                    price_after_tax, price_before_tax, sales_rank, created_on, created_by, last_updated_on, last_updated_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, [
                client_id,
                data['name'],
                data['HSN_code'],
                data['tax_percentage'],
                data['discount_rate'],
                data['unit'],
                data.get('category', None),
                data.get('brand', None),
                data['price_after_tax'],
                data['price_before_tax'],
                data.get('sales_rank', None),
                timezone.now(),
                data['created_by'],
                timezone.now(),
                username
            ])

        return JsonResponse({"message": "Product added successfully."}, status=201)

    def put(self, request):
        client_id = self.get_client_id_from_cookie(request)
        username = self.get_username_from_cookie(request)
        if isinstance(client_id, JsonResponse):
            return client_id

        data = json.loads(request.body)
        product_id = data.get("product_id")
        if not product_id:
            return JsonResponse({"error": "product_id is required for updating a product."}, status=400)

        # Check if the product exists
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Product WHERE product_id = %s AND client_id = %s", [product_id, client_id])
            product = cursor.fetchone()
            if not product:
                return JsonResponse({"error": "Product not found or not authorized to modify this product."},
                                    status=404)

        # Prepare SQL query to update only the fields that have been provided
        sql_query = """
            UPDATE Product
            SET name = %s, HSN_code = %s, tax_percentage = %s, discount_rate = %s, unit = %s, category = %s, brand = %s, 
                price_after_tax = %s, price_before_tax = %s, sales_rank = %s, last_updated_on = %s, last_updated_by = %s
            WHERE product_id = %s AND client_id = %s
        """

        params = [
            data['name'],
            data['HSN_code'],
            data['tax_percentage'],
            data['discount_rate'],
            data['unit'],
            data.get('category', None),
            data.get('brand', None),
            data['price_after_tax'],
            data['price_before_tax'],
            data.get('sales_rank', None),
            timezone.now(),
            username,
            product_id,
            client_id
        ]

        with connection.cursor() as cursor:
            cursor.execute(sql_query, params)

        return JsonResponse({"message": "Product updated successfully."}, status=200)

    def delete(self, request):
        client_id = self.get_client_id_from_cookie(request)
        if isinstance(client_id, JsonResponse):
            return client_id

        data = json.loads(request.body)
        product_id = data.get("product_id")
        if not product_id:
            return JsonResponse({"error": "product_id is required for deleting a product."}, status=400)

        # Verify product exists before attempting deletion
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Product WHERE product_id = %s AND client_id = %s", [product_id, client_id])
            product = cursor.fetchone()
            if not product:
                return JsonResponse({"error": "Product not found or not authorized to delete this product."},
                                    status=404)

        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM Product WHERE product_id = %s AND client_id = %s", [product_id, client_id])

        return JsonResponse({"message": "Product deleted successfully."}, status=200)

# customer end points start here
@method_decorator(csrf_exempt, name='dispatch')
class CustomerView(View):
    permission_classes = [IsAuthenticated]

    def get_client_id_from_cookie(self, request):
        client_id = request.client_id
        if not client_id:
            return JsonResponse({"error": "client_id is missing from cookies."}, status=400)
        return client_id

    def get_username_from_cookie(self, request):
        username = request.username
        if not username:
            return JsonResponse({"error": "username is missing from cookies."}, status=400)
        return username

    def get(self, request):
        client_id = self.get_client_id_from_cookie(request)
        if isinstance(client_id, JsonResponse):
            return client_id

        # Get query parameters for search and filtering
        search_query = request.GET.get('search', '')

        # Base SQL query for fetching customers
        sql_query = "SELECT customer_id,name,address,phone,email_id,category,gstin,sales_rank FROM Customer WHERE client_id = %s"
        params = [client_id]

        # Apply search filter if provided
        if search_query:
            sql_query += " AND name LIKE %s"
            params.append(f"%{search_query}%")

        # Order by customer_id
        sql_query += " ORDER BY customer_id"

        # Fetch customers
        with connection.cursor() as cursor:
            cursor.execute(sql_query, params)
            customers = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            customer_list = [dict(zip(columns, customer)) for customer in customers]

        return JsonResponse({
            "customers": customer_list
        }, status=200)

    def post(self, request):
        client_id = self.get_client_id_from_cookie(request)
        username = self.get_username_from_cookie(request)
        if isinstance(client_id, JsonResponse):
            return client_id

        data = json.loads(request.body)
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO Customer (client_id, name, address, phone, email_id, category, GSTIN, password, otp, 
                    sales_rank, created_on, created_by, last_updated_on, last_updated_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, [
                client_id,
                data['name'],
                data.get('address', None),
                data['phone'],
                data.get('email_id', None),
                data['category'],
                data.get('GSTIN', None),
                data.get('password', None),
                data.get('otp', None),
                data.get('sales_rank', None),
                timezone.now(),
                username,
                timezone.now(),
                username
            ])

        return JsonResponse({"message": "Customer added successfully."}, status=201)

    def put(self, request):
        client_id = self.get_client_id_from_cookie(request)
        username = self.get_username_from_cookie(request)
        if isinstance(client_id, JsonResponse):
            return client_id

        data = json.loads(request.body)
        customer_id = data.get("customer_id")
        if not customer_id:
            return JsonResponse({"error": "customer_id is required for updating a customer."}, status=400)

        # Check if the customer exists
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Customer WHERE customer_id = %s AND client_id = %s", [customer_id, client_id])
            customer = cursor.fetchone()
            if not customer:
                return JsonResponse({"error": "Customer not found or not authorized to modify this customer."},
                                    status=404)

        # Prepare SQL query to update only the fields that have been provided
        sql_query = """
            UPDATE Customer
            SET name = %s, address = %s, phone = %s, email_id = %s, category = %s, GSTIN = %s, 
                password = %s, otp = %s, sales_rank = %s, last_updated_on = %s, last_updated_by = %s
            WHERE customer_id = %s AND client_id = %s
        """

        params = [
            data['name'],
            data.get('address', None),
            data['phone'],
            data.get('email_id', None),
            data['category'],
            data.get('GSTIN', None),
            data.get('password', None),
            data.get('otp', None),
            data.get('sales_rank', None),
            timezone.now(),
            username,
            customer_id,
            client_id
        ]

        with connection.cursor() as cursor:
            cursor.execute(sql_query, params)

        return JsonResponse({"message": "Customer updated successfully."}, status=200)

    def delete(self, request):
        client_id = self.get_client_id_from_cookie(request)
        if isinstance(client_id, JsonResponse):
            return client_id

        data = json.loads(request.body)
        customer_id = data.get("customer_id")
        if not customer_id:
            return JsonResponse({"error": "customer_id is required for deleting a customer."}, status=400)

        # Verify customer exists before attempting deletion
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Customer WHERE customer_id = %s AND client_id = %s", [customer_id, client_id])
            customer = cursor.fetchone()
            if not customer:
                return JsonResponse({"error": "Customer not found or not authorized to delete this customer."},
                                    status=404)

        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM Customer WHERE customer_id = %s AND client_id = %s", [customer_id, client_id])

        return JsonResponse({"message": "Customer deleted successfully."}, status=200)

# For getting client information for billing
class ClientPlaceOfSupplyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        client_id = request.COOKIES.get('client_id')
        if not client_id:
            return JsonResponse({"message": "Client ID missing from cookies"}, status=400)

        # Fetch the client's place of supply
        with connection.cursor() as cursor:
            cursor.execute("SELECT place_of_supply FROM billing_app_client WHERE client_id = %s", [client_id])
            result = cursor.fetchone()

        if result:
            return JsonResponse({"place_of_supply": result[0]}, status=200)
        else:
            return JsonResponse({"message": "Place of supply not found for the client"}, status=404)