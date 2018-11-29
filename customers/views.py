from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny

from .serializers import CustomerSerializer
from .models import Customer


class CustomerViewSet(mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      viewsets.GenericViewSet):
    queryset = Customer.objects.filter(is_deleted=False).order_by('-created')
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return super(CustomerViewSet, self).get_permissions()