from rest_framework.permissions import BasePermission

class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'

class IsManagerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ('admin','manager')

class IsOwnerOrManagerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role in ('admin','manager'):
            return True
        return hasattr(obj, 'user') and obj.user == request.user or \
               hasattr(obj, 'assigned_to') and obj.assigned_to == request.user
