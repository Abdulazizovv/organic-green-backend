"""
Custom throttling classes for the API
"""
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class AuthRateThrottle(AnonRateThrottle):
    """
    Throttle for authentication endpoints only.
    More restrictive to prevent brute force attacks.
    """
    scope = 'auth'


class BurstRateThrottle(AnonRateThrottle):
    """
    Throttle for burst protection on specific endpoints.
    """
    scope = 'burst'


class LenientUserRateThrottle(UserRateThrottle):
    """
    Very lenient throttle for authenticated users.
    Only kicks in for extreme abuse.
    """
    scope = 'user'
    
    def allow_request(self, request, view):
        """
        Override to be more lenient for authenticated users
        """
        if request.user and request.user.is_authenticated:
            # Much more lenient for authenticated users
            return super().allow_request(request, view)
        return True  # No throttling for authenticated users in normal cases


class LenientAnonRateThrottle(AnonRateThrottle):
    """
    More lenient throttle for anonymous users.
    """
    scope = 'anon'
