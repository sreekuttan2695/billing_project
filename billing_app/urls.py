from django.urls import path
from .views import (CustomUserLoginView, CustomTokenRefreshView, CustomUserLogoutView,
                    CreateUserView, CreateClientView, ProtectedView, ProductView, CustomerView,
                    ClientPlaceOfSupplyView, CreateBillView, ChangeBillView, VendorManagement)

urlpatterns = [
    path('api/login/', CustomUserLoginView.as_view(), name='custom-user-login'),
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='custom-token-refresh'),
    path('api/logout/', CustomUserLogoutView.as_view(), name='custom-user-logout'),
    path('api/create-user/', CreateUserView.as_view(), name='create-user'),
    path('api/create-client/', CreateClientView.as_view(), name='create-client'),
    path('protected/', ProtectedView.as_view(), name='protected-view'),
    path('api/product/', ProductView.as_view(), name='product-endpoint'),
    path('api/customer/', CustomerView.as_view(), name='customer'),
    path("api/client/place_of_supply/", ClientPlaceOfSupplyView.as_view(), name="client-place-of-supply"),
    path("api/create-bill/", CreateBillView.as_view(), name="client-place-of-supply"),
    path('api/change-bill/', ChangeBillView.as_view(), name='change-bill'),
    path('api/vendor-management/', VendorManagement.as_view(), name='vendor-management'),

   # path('api/create-client/', ClientCreateView.as_view(), name='create-client'),
]
