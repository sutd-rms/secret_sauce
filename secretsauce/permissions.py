from rest_framework import permissions
from secretsauce.apps.account.models import User
from secretsauce.apps.portal.models import *

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Only give permissions to owners and admins
    """

    def has_object_permission(self, request, view, obj):
        # Gives permission only to owners, instance must have attribute named owners.
        if request.user.is_superuser:
            return True

        if isinstance(obj, Project):
            return obj.owners.all().filter(pk=request.user.email).exists()

        if isinstance(obj, DataBlock) or isinstance(obj, ConstraintBlock):
            return obj.project.owners.all().filter(pk=request.user.email).exists()

        if isinstance(obj, Constraint) or isinstance(obj, ConstraintParameter):
            return obj.constraint_block.project.owners.all().filter(pk=request.user.email).exists()

        if isinstance(obj, ConstraintParameterRelationship):
            return obje.constraint.constraint_block.project.owners.all().filter(pk=request.user.email).exists()
        
        return False
        
    
class AdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        return request.method in permissions.SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return True
        