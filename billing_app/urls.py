from django.urls import path
from .views import ProtectedView, CookieTokenObtainView, CookieTokenRefreshView, LogoutView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('api/token/', CookieTokenObtainView.as_view(), name='token_obtain'),
    path('api/token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('protected-view/', ProtectedView.as_view(), name='protected-view'),
]
