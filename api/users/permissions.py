from rest_framework.permissions import BasePermission
from django.conf import settings


# Custom permission for users in token is exists.
class IsTokenValid(BasePermission):
    """
    Allows access only to user in token is exists.
    """
    message = {'message': 'Token is invalid or expired.'}
    
    def has_permission(self, request, view):
        return request.user and request.user.token is not None