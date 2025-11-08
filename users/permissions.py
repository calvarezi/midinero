from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    """
    Permite acceso solo al dueño del objeto.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permite escritura solo a administradores, lectura a todos.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff
