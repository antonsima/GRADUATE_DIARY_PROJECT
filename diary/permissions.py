from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешение, позволяющее только владельцу объекта редактировать его.
    """

    def has_object_permission(self, request, view, obj):
        # Чтение разрешено для всех запросов
        if request.method in permissions.SAFE_METHODS:
            return True

        # Запись разрешена только владельцу
        return obj.owner == request.user