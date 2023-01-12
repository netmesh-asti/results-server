from rest_framework import permissions


class IsAuthenticatedOrPostOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        else:
            return True


class IsAdminFull(permissions.BasePermission):
    """
        Only admin can create, authenticated users
        can read only
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return request.user.is_staff
