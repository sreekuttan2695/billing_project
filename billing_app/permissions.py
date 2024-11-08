from rest_framework.permissions import BasePermission

class IsSuperAdminUser(BasePermission):
    """
    Allows access only to superusers or specific admin users (e.g., "superadmin").
    """
    def has_permission(self, request, view):
        # Check if the user is authenticated and is a superuser or has the username "superadmin"
        return request.user.is_authenticated and (request.user.is_superuser or request.user.username == "superadmin")
