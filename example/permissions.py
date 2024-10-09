from rest_framework.permissions import BasePermission, SAFE_METHODS



class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Only allow the owner of the object to modify it
        return obj.user == request.user


class IsProfessionalOrReadOnly(BasePermission):
    """
    Custom permission to allow only read-only actions (GET) for professionals.
    Non-professionals will have full access.
    """

    def has_permission(self, request, view):
        # Allow read-only access (GET, HEAD, OPTIONS) for professionals
        if request.method in SAFE_METHODS:
            # Check if the user is a professional
            return request.user.is_authenticated and hasattr(request.user, 'professional')
        # Non-professionals have full access (if authenticated)
        return request.user.is_authenticated
