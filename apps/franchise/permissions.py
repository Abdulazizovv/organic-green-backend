"""
Franchise application permissions
"""
from rest_framework.permissions import BasePermission


class FranchiseApplicationPermission(BasePermission):
    """
    Custom permission for franchise applications:
    - Anyone can create (POST)
    - Only staff/admin can list, view, update, delete
    """

    def has_permission(self, request, view):
        # Allow POST (create) for everyone
        if request.method == 'POST':
            return True
        
        # For all other methods, require staff permission
        return request.user and request.user.is_authenticated and request.user.is_staff

    def has_object_permission(self, request, view, obj):
        # For object-level permissions, require staff
        return request.user and request.user.is_authenticated and request.user.is_staff
