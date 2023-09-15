from rest_framework.permissions import BasePermission


class IsObjectOwner(BasePermission):

    # check obj.user == request.user
    # if detail=False, will check has_permission
    # if detail=True, will check both has_permission and has_object_permission

    message = 'You do not have permission to access this object'

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user
