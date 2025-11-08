from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permite edición solo al dueño del objeto; lectura para otros autenticados.
    Asume que el objeto tiene un atributo `user` (FK al owner).
    """

    def has_object_permission(self, request, view, obj):
        # Lectura para métodos SAFE
        if request.method in permissions.SAFE_METHODS:
            return True
        # Escritura solo si el objeto pertenece al usuario
        return hasattr(obj, 'user') and obj.user == request.user

class IsStaffOrOwner(permissions.BasePermission):
    """
    Permite acceso si el usuario es staff (admin) o si es owner del objeto.
    """

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        return hasattr(obj, 'user') and obj.user == request.user
