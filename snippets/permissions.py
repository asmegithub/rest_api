from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Allow GET, HEAD, and OPTIONS requests for anyone.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Allow write permissions (POST, PUT, DELETE) only for the owner.
        return obj.owner == request.user
