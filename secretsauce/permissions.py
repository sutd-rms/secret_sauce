from rest_framework import permissions
from secretsauce.apps.account.models import User
from secretsauce.apps.portal.models import Project

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Only give permissions to owners 
    """

    def has_object_permission(self, request, view, obj):
        # Gives permission only to owners, instance must have attribute named owners.
        return obj.owners.all().filter(pk=request.user.email).exists() or request.user.is_superuser
    
class AdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or request.user.is_superuser
        