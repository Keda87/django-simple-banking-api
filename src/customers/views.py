from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from cores.permissions import IsCustomer
from .models import Customer
from .serializers import CustomerSerializer


class CustomerViewSet(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    queryset = Customer.objects.filter(is_deleted=False).order_by('-created')
    serializer_class = CustomerSerializer
    permission_classes = [IsCustomer]

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return super(CustomerViewSet, self).get_permissions()

    def list(self, request, *args, **kwargs):
        customer = request.user.customer
        serializer = self.get_serializer(instance=customer)

        return Response(serializer.data)
