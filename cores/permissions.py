from rest_framework.permissions import IsAuthenticated


class IsCustomer(IsAuthenticated):

    def has_permission(self, request, view):
        authenticated = super(IsCustomer, self).has_permission(request, view)
        return authenticated and hasattr(request.user, 'customer')


class IsCustomerBank(IsCustomer):

    def has_object_permission(self, request, view, obj):
        return obj.holder == request.user.customer
