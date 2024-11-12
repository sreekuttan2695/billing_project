from django.urls import path
from .views import (CustomUserLoginView, CustomTokenRefreshView, CustomUserLogoutView,
                    CreateUserView, CreateClientView, ProtectedView, ProductView, CustomerView)

urlpatterns = [
    path('api/login/', CustomUserLoginView.as_view(), name='custom-user-login'),
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='custom-token-refresh'),
    path('api/logout/', CustomUserLogoutView.as_view(), name='custom-user-logout'),
    path('api/create-user/', CreateUserView.as_view(), name='create-user'),
    path('api/create-client/', CreateClientView.as_view(), name='create-client'),
    path('protected/', ProtectedView.as_view(), name='protected-view'),
    path('api/product/', ProductView.as_view(), name='product-endpoint'),
    path('api/customer/', CustomerView.as_view(), name='customer'),
   # path('api/create-client/', ClientCreateView.as_view(), name='create-client'),
]
