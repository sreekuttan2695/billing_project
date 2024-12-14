from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser, CustomerBill, BillItem, BillTaxSplit, Customer, Client, Product
from django.contrib.auth import authenticate
from django.db import transaction
from .serializers import (CustomUserSerializer, ClientSerializer, ProductSerializer,
                          BillItemSerializer, CustomerBillSerializer, BillTaxSplitSerializer)
from .permissions import IsSuperAdminUser
from django.views import View
from django.http import JsonResponse
from django.db import connection
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import random
import string
from datetime import datetime

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
                samesite='None'
            )
            response.set_cookie(
                key='refresh_token',
                value=str(refresh),
                httponly=True,
                secure=True,
                samesite='None'
            )
            response.set_cookie(
                key='client_id',
                value=client_id,
                httponly=True,
                secure=True,
                samesite='None'
            )

            response.set_cookie(
                key='username',
                value=username,
                httponly=True,
                secure=True,
                samesite='None'
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
@method_decorator(csrf_exempt, name='dispatch')
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

@method_decorator(csrf_exempt, name='dispatch')
class CreateBillView(APIView):
    permission_classes = [IsAuthenticated]  # Ensures only authenticated users can access

    def get_client_id_from_cookie(self, request):
        # Assuming client_id is stored in cookies
        client_id = request.COOKIES.get("client_id")
        if not client_id:
            return Response({"error": "client_id is missing from cookies."}, status=400)
        return client_id

    def get_username_from_cookie(self, request):
        # Assuming username is stored in cookies
        username = request.COOKIES.get("username")
        if not username:
            return Response({"error": "username is missing from cookies."}, status=400)
        return username

    def generate_unique_invoice_no(self, client_id):
        while True:
            # Generate a random 3-character text (uppercase letters only)
            random_text = ''.join(random.choices(string.ascii_uppercase, k=3))

            # Generate a random 3-digit number
            random_number = ''.join(random.choices(string.digits, k=3))

            # Get the current year in YY format
            year = datetime.now().strftime('%y')

            # Concatenate to form the invoice number
            invoice_no = f"{year}{random_text}{random_number}"

            # Check if the generated invoice_no already exists for the client_id
            if not CustomerBill.objects.filter(client_id=client_id, invoice_no=invoice_no).exists():
                return invoice_no

    def post(self, request, *args, **kwargs):
        """
        Handles the creation of a new bill by inserting data into Customer_Bill, Bill_Items, and Bill_Tax_Splits.
        """
        data = request.data

        # Get client_id and username from cookies
        client_id = self.get_client_id_from_cookie(request)
        username = self.get_username_from_cookie(request)

        if isinstance(client_id, Response) or isinstance(username, Response):
            return client_id or username

        # Fetch customer_id using customer_name and client_id
        customer_name = data.get("customer_name")
        if not customer_name:
            return Response({"error": "Customer name is required."}, status=400)

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT customer_id FROM Customer WHERE name = %s AND client_id = %s",
                [customer_name, client_id]
            )
            customer_id = cursor.fetchone()
            if not customer_id:
                return Response({"error": f"Customer '{customer_name}' not found."}, status=400)
            customer_id = customer_id[0]  # Extract customer_id from tuple

        invoice_no = self.generate_unique_invoice_no(client_id)

        try:
            with transaction.atomic():
                # Insert into Customer_Bill
                customer_bill = CustomerBill.objects.create(
                    customer=Customer.objects.get(customer_id=customer_id),  # ForeignKey to Customer
                    client=Client.objects.get(client_id=client_id),  # ForeignKey to Client - passing this and customer as instance rather than just ids
                    invoice_no=invoice_no,  # You should generate this dynamically
                    invoice_date=data["invoice_date"],
                    place_of_supply=data["place_of_supply"],
                    total_amount_before_tax=data["total_amount_before_tax"],
                    discount=data["discount"],
                    total_amount=data["total_amount"],
                    status=data["status"],
                    is_rcm=data["is_rcm"],
                    created_by=username,
                    created_on=timezone.now(),
                    last_updated_by=username
                )

                # Insert into Bill_Items
                for item in data["bill_items"]:
                    product_name = item.get("product_name")
                    if not product_name:
                        return Response({"error": "Product name is required for each bill item."}, status=400)

                    # Fetch product instance using product_name and client_id
                    try:
                        product = Product.objects.get(name=product_name, client_id=client_id)
                    except Product.DoesNotExist:
                        return Response({"error": f"Product '{product_name}' not found."}, status=400)

                    # Insert item into Bill_Items table
                    BillItem.objects.create(
                        bill=customer_bill,  # ForeignKey to CustomerBill
                        client=Client.objects.get(client_id=client_id),  # ForeignKey to Client
                        product=product,  # ForeignKey to Product
                        qty=item["qty"],
                        unit=item["unit"],
                        price=item["price"],
                        discount=item["discount"],
                        tax_rate=item["tax_rate"],
                        taxable_amount=item["taxable_amount"],
                        total_amount=item["total_amount"],
                        created_by=username,
                        created_on=timezone.now(),
                        last_updated_by=username,
                    )

                # Insert into Bill_Tax_Splits
                for tax in data["bill_tax_splits"]:
                    BillTaxSplit.objects.create(
                        bill=customer_bill,  # ForeignKey to CustomerBill
                        tax_rate=tax["tax_rate"],
                        SGST=tax["SGST"],
                        CGST=tax["CGST"],
                        IGST=tax["IGST"],
                        CESS=tax.get("CESS", 0.0),  # Default to 0.0 if CESS is not provided
                        created_by=username,
                        created_on=timezone.now(),
                        last_updated_by=username,
                    )

            return Response(
                {"message": "Bill created successfully!", "invoice_no": customer_bill.invoice_no},
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            print(f"Error in CreateBillView: {e}")
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request, *args, **kwargs):
        """
        Fetch the latest invoice details with optional filters for customer name and invoice number.
        """
        client_id = self.get_client_id_from_cookie(request)
        if isinstance(client_id, Response):
            return client_id

        # Retrieve query parameters for filters
        customer_name_filter = request.GET.get("customer_name", "")
        invoice_no_filter = request.GET.get("invoice_no", "")

        try:
            # Base SQL query
            sql_query = """
                SELECT b.invoice_no, b.invoice_date, c.name AS customer_name, 
                       b.total_amount, b.status, b.last_updated_on
                FROM billing_app_customerbill b
                INNER JOIN customer c ON c.client_id = b.client_id AND c.customer_id = b.customer_id
                WHERE b.client_id = %s 
                AND (b.invoice_no LIKE %s AND c.name LIKE %s)
                ORDER BY b.last_updated_on DESC 
                LIMIT 10
            """
            params = [client_id, f"%{invoice_no_filter}%", f"%{customer_name_filter}%"]

            # Execute query
            with connection.cursor() as cursor:
                cursor.execute(sql_query, params)
                rows = cursor.fetchall()
                columns = [col[0] for col in cursor.description]
                invoices = [dict(zip(columns, row)) for row in rows]

            return Response({"invoices": invoices}, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error fetching billing management data: {e}")
            return Response(
                {"error": "An error occurred while fetching billing management data."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@method_decorator(csrf_exempt, name='dispatch')
class ChangeBillView(APIView):
    permission_classes = [IsAuthenticated]

    def get_client_id_from_cookie(self, request):
        # Assuming client_id is stored in cookies
        client_id = request.COOKIES.get("client_id")
        if not client_id:
            return Response({"error": "client_id is missing from cookies."}, status=400)
        return client_id

    def get(self, request, *args, **kwargs):
        """
        Fetch detailed bill information for a given invoice number.
        """
        client_id = self.get_client_id_from_cookie(request)
        if isinstance(client_id, Response):
            return client_id

        # Retrieve the invoice number from the query parameters
        invoice_no = request.GET.get("invoice_no")
        if not invoice_no:
            return Response({"error": "Invoice number is required."}, status=400)

        try:
            # Query 1: Fetch customer and basic bill details
            bill_details_query = """
                SELECT b.invoice_no, c.name, c.phone, c.address, c.GSTIN,
                       b.place_of_supply, b.invoice_date, b.is_rcm, 
                       b.total_amount_before_tax, b.discount, b.total_amount, b.status, b.bill_id
                FROM billing_app_customerbill b
                INNER JOIN customer c ON b.customer_id = c.customer_id
                WHERE b.invoice_no = %s AND b.client_id = %s
            """
            with connection.cursor() as cursor:
                cursor.execute(bill_details_query, [invoice_no, client_id])
                bill_details = cursor.fetchone()

            if not bill_details:
                return Response({"error": "No bill found for the provided invoice number."}, status=404)

            # Query 2: Fetch product details
            product_details_query = """
                SELECT p.name, b.qty, b.unit, b.price, b.discount, 
                       b.tax_rate, b.taxable_amount, b.total_amount, b.bill_item_id
                FROM billing_app_billitem b
                INNER JOIN product p ON b.product_id = p.product_id
                WHERE b.bill_id IN (
                    SELECT bill_id FROM billing_app_customerbill WHERE invoice_no = %s AND client_id = %s
                )
            """
            with connection.cursor() as cursor:
                cursor.execute(product_details_query, [invoice_no, client_id])
                product_details = cursor.fetchall()

            # Query 3: Fetch tax split details
            tax_split_query = """
                SELECT t.tax_rate, t.SGST, t.CGST, t.IGST, t.CESS, t.bts_id
                FROM billing_app_billtaxsplit t
                INNER JOIN billing_app_customerbill b ON t.bill_id = b.bill_id
                WHERE b.invoice_no = %s AND b.client_id = %s
            """
            with connection.cursor() as cursor:
                cursor.execute(tax_split_query, [invoice_no, client_id])
                tax_split_details = cursor.fetchall()

            # Construct the response
            response_data = {
                "bill_details": dict(zip(
                    ["invoice_no", "name", "phone", "address", "GSTIN",
                     "place_of_supply", "invoice_date", "is_rcm",
                     "total_amount_before_tax", "discount", "total_amount", "status", "bill_id"],
                    bill_details
                )),
                "product_details": [
                    dict(zip(["name", "qty", "unit", "price", "discount", "tax_rate", "taxable_amount", "total_amount", "bill_item_id"], row))
                    for row in product_details
                ],
                "tax_split_details": [
                    dict(zip(["tax_rate", "SGST", "CGST", "IGST", "CESS", "bts_id"], row))
                    for row in tax_split_details
                ]
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error fetching bill details: {e}")
            return Response({"error": "An error occurred while fetching bill details."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, *args, **kwargs):
        data = request.data
        invoice_no = data.get("invoice_no")

        if not invoice_no:
            return Response({"error": "Invoice number is required."}, status=400)

        client_id = self.get_client_id_from_cookie(request)
        if isinstance(client_id, Response):
            return client_id

        # Fetch bill details to validate existence
        try:
            customer_bill = CustomerBill.objects.get(invoice_no=invoice_no, client_id=client_id)
        except CustomerBill.DoesNotExist:
            return Response({"error": "Invoice not found."}, status=404)

        try:
            with transaction.atomic():
                # Update customer_id if the customer name is changed
                customer_name = data.get("customer_name")
                if customer_name:
                    with connection.cursor() as cursor:
                        cursor.execute(
                            "SELECT customer_id FROM Customer WHERE name = %s AND client_id = %s",
                            [customer_name, client_id],
                        )
                        customer_id = cursor.fetchone()
                        if not customer_id:
                            return Response({"error": f"Customer '{customer_name}' not found."}, status=400)

                        customer_bill.customer_id = customer_id[0]
                        customer_bill.save()

                # Update, delete bill items (no insertion allowed)
                for item in data["bill_items"]:
                    if item.get("action") == "delete":
                        BillItem.objects.filter(bill=customer_bill, bill_item_id=item["bill_item_id"]).delete()
                    elif item.get("action") == "update":
                        bill_item = BillItem.objects.get(bill_item_id=item["bill_item_id"], bill=customer_bill)
                        bill_item.qty = item["qty"]
                        bill_item.unit = item["unit"]
                        bill_item.price = item["price"]
                        bill_item.discount = item["discount"]
                        bill_item.tax_rate = item["tax_rate"]
                        bill_item.taxable_amount = item["taxable_amount"]
                        bill_item.total_amount = item["total_amount"]
                        bill_item.save()

                # Update tax splits
                # BillTaxSplit.objects.filter(bill=customer_bill).delete()
                for tax in data["bill_tax_splits"]:
                    # BillTaxSplit.objects.create(
                    #     bill=customer_bill,
                    #     tax_rate=tax["tax_rate"],
                    #     SGST=tax["SGST"],
                    #     CGST=tax["CGST"],
                    #     IGST=tax["IGST"],
                    #     CESS=tax.get("CESS", 0.0),
                    # )
                    bill_tax_split = BillTaxSplit.objects.get(bts_id=tax["bts_id"])
                    bill_tax_split.tax_rate = tax["tax_rate"]
                    bill_tax_split.SGST = tax["SGST"]
                    bill_tax_split.CGST = tax["CGST"]
                    bill_tax_split.IGST = tax["IGST"]
                    bill_tax_split.CESS = tax["CESS"]
                    bill_tax_split.save()

                # Update main bill details
                customer_bill.total_amount_before_tax = data["total_amount_before_tax"]
                customer_bill.discount = data["discount"]
                customer_bill.total_amount = data["total_amount"]
                customer_bill.is_rcm = data["is_rcm"]
                customer_bill.status = data["status"]
                customer_bill.save()

            return Response({"message": "Bill updated successfully."}, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
