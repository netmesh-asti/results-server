from rest_framework import permissions


class IsAuthenticatedOrPostOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        else:
            return True
