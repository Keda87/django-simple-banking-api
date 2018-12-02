from rest_framework import serializers

from customers.models import Customer
from .models import BankInformation, BankStatement


class AccountSerializer(serializers.ModelSerializer):
    holder = serializers.CharField(source='holder.user.get_full_name')
    balance = serializers.DecimalField(
        source='total_balance',
        decimal_places=2,
        max_digits=12,
    )

    class Meta:
        model = BankInformation
        fields = [
            'id', 'guid', 'account_number', 'holder', 'is_active', 'balance'
        ]


class TransactionSerializer(serializers.ModelSerializer):
    bank_info = serializers.CharField(source='bank_info.account_number')
    sender = serializers.CharField(source='sender.user.get_full_name')
    receiver = serializers.CharField(source='receiver.user.get_full_name')

    class Meta:
        model = BankStatement
        fields = [
            'id', 'bank_info', 'sender', 'receiver', 'amount', 'is_debit',
        ]


class DepositTransactionSerializer(serializers.Serializer):
    sender = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.filter(is_deleted=False),
    )
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)

    def validate(self, attrs):
        sender = attrs.get('sender')
        if not sender.bankinformation.is_active:
            raise serializers.ValidationError({
                'sender': 'Bank account is blocked or inactive.'
            })
        return attrs

    def create(self, validated_data):
        sender = validated_data.get('sender')
        deposit_amount = validated_data.get('amount')

        deposit = BankStatement()
        deposit.bank_info = sender.bankinformation
        deposit.sender = sender
        deposit.receiver = sender
        deposit.amount = deposit_amount
        deposit.is_debit = False
        deposit.save()

        serializer = TransactionSerializer(instance=deposit)
        return serializer.data
