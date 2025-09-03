"""
Order permissions for Organic Green e-commerce
"""
from rest_framework.permissions import BasePermission


class IsOrderOwner(BasePermission):
    """
    Custom permission to only allow owners of an order to view/edit it.
    
    For authenticated users: must be the order owner
    For anonymous users: session_key must match
    """
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user has permission to access the order
        """
        # For authenticated users - check if they own the order
        if request.user.is_authenticated:
            return obj.user == request.user
        
        # For anonymous users - check session key match
        if not request.user.is_authenticated and obj.session_key:
            # Get session key from request
            session_key = request.session.session_key
            
            # Also check X-Session-Key header (for custom session handling)
            header_session_key = request.headers.get('X-Session-Key')
            
            return (
                obj.session_key == session_key or 
                obj.session_key == header_session_key
            )
        
        return False


class IsOrderOwnerOrReadOnly(IsOrderOwner):
    """
    Custom permission to allow read access to order owners
    and write access only for specific actions
    """
    
    def has_permission(self, request, view):
        """
        Allow any authenticated user or anonymous user to access order endpoints
        Object-level permissions will be checked in has_object_permission
        """
        return True
    
    def has_object_permission(self, request, view, obj):
        """
        Read permissions for order owners
        Write permissions for specific safe actions only
        """
        # Check if user is owner first
        is_owner = super().has_object_permission(request, view, obj)
        
        if not is_owner:
            return False
        
        # Allow read access for owners
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        # Allow specific write actions (like cancel)
        if view.action in ['cancel']:
            return True
        
        # Deny other write access (orders shouldn't be editable after creation)
        return False
