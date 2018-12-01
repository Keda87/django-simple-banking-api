from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response

from cores.permissions import IsCustomerBank, IsCustomer
from .models import BankInformation
from .serializers import AccountSerializer


class BankInformationViewSet(mixins.ListModelMixin,
                             viewsets.GenericViewSet):
    serializer_class = AccountSerializer
    permission_classes = [IsCustomer]
    queryset = BankInformation.objects.filter(is_deleted=False)
    lookup_field = 'guid'

    def list(self, request, *args, **kwargs):
        customer = request.user.customer
        bank_info = customer.bankinformation
        data = self.get_serializer(instance=bank_info).data
        return Response(data)

    @action(methods=['put'], detail=True, permission_classes=[IsCustomerBank])
    def activate(self, request, **kwargs):
        bank_info = self.get_object()
        bank_info.is_active = True
        bank_info.save()
        return Response(status=status.HTTP_200_OK)

    @action(methods=['put'], detail=True, permission_classes=[IsCustomerBank])
    def deactivate(self, request, **kwargs):
        bank_info = self.get_object()
        bank_info.is_active = False
        bank_info.save()
        return Response(status=status.HTTP_200_OK)

