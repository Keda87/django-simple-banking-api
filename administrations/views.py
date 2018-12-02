from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response

from cores.permissions import IsBankOwner, IsCustomer
from .models import BankInformation, BankStatement
from .serializers import AccountSerializer, DepositTransactionSerializer


class BankInformationViewSet(mixins.ListModelMixin,
                             viewsets.GenericViewSet):
    serializer_class = AccountSerializer
    permission_classes = [IsCustomer]
    queryset = BankInformation.objects.filter(is_deleted=False)
    lookup_field = 'guid'

    def get_queryset(self):
        queryet = super(BankInformationViewSet, self).get_queryset()
        return queryet.filter(holder=self.request.user.customer)

    def list(self, request, *args, **kwargs):
        customer = request.user.customer
        bank_info = customer.bankinformation
        data = self.get_serializer(instance=bank_info).data
        return Response(data)

    @action(methods=['put'], detail=True, permission_classes=[IsBankOwner])
    def activate(self, request, **kwargs):
        bank_info = self.get_object()
        bank_info.is_active = True
        bank_info.save()
        return Response(status=status.HTTP_200_OK)

    @action(methods=['put'], detail=True, permission_classes=[IsBankOwner])
    def deactivate(self, request, **kwargs):
        bank_info = self.get_object()
        bank_info.is_active = False
        bank_info.save()
        return Response(status=status.HTTP_200_OK)


class DepositViewSet(mixins.CreateModelMixin,
                     viewsets.GenericViewSet):
    serializer_class = DepositTransactionSerializer
    permission_classes = [IsCustomer]
    queryset = BankStatement.objects.filter(is_deleted=False)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['sender'] = request.user.customer.pk
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            response = serializer.save()
            return Response(response, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class TransferViewSet(mixins.CreateModelMixin,
                      viewsets.GenericViewSet):
    pass
