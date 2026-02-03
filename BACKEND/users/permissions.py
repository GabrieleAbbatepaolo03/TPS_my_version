from rest_framework import permissions


class IsCustomer(permissions.BasePermission):
    """
    Permission class that only allows customer user type.
    """
    message = 'Access denied. Only customers can access this resource.'
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type == 'customer'
        )


class IsOfficer(permissions.BasePermission):
    """
    Permission class that only allows officer user type.
    """
    message = 'Access denied. Only officers can access this resource.'
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type == 'officer'
        )


class IsManager(permissions.BasePermission):
    """
    Permission class that only allows manager user type.
    """
    message = 'Access denied. Only managers can access this resource.'
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type == 'manager'
        )


class IsOfficerOrManager(permissions.BasePermission):
    """
    Permission class that allows officer or manager user types.
    """
    message = 'Access denied. Only officers or managers can access this resource.'
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type in ['officer', 'manager']
        )
