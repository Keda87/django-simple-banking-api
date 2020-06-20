from django.db import transaction
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
        deposit.description = 'Amount deposit'
        deposit.save()

        serializer = TransactionSerializer(instance=deposit)
        return serializer.data


class WithdrawSerializer(DepositTransactionSerializer):

    @transaction.atomic
    def create(self, validated_data):
        sender = validated_data.get('sender')
        deposit_amount = validated_data.get('amount')

        sender_bank = BankInformation.objects.select_for_update().get(
            pk=sender.bankinformation.pk,
        )

        if sender_bank.total_balance < deposit_amount:
            raise serializers.ValidationError({
                'amount': 'Insufficient funds.'
            })

        deposit = BankStatement()
        deposit.bank_info = sender.bankinformation
        deposit.sender = sender
        deposit.receiver = sender
        deposit.amount = deposit_amount
        deposit.is_debit = True
        deposit.description = 'Amount withdrawn'
        deposit.save()

        serializer = TransactionSerializer(instance=deposit)
        return serializer.data


class TransferTransactionSerializer(serializers.Serializer):
    sender = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.filter(is_deleted=False),
    )
    destination_account_number = serializers.CharField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)

    @transaction.atomic
    def create(self, validated_data):
        sender = validated_data.get('sender')
        amount = validated_data.get('amount')
        account_number = validated_data.get('destination_account_number')

        try:
            receiver_bank = BankInformation.objects.select_for_update().get(
                account_number=account_number,
            )
        except BankInformation.DoesNotExist:
            raise serializers.ValidationError({
                'destination_account_number': 'Invalid account number.'
            })

        if not receiver_bank.is_active:
            raise serializers.ValidationError({
                'receiver': 'Bank account is blocked or inactive.'
            })

        if not sender.bankinformation.is_active:
            raise serializers.ValidationError({
                'sender': 'Bank account is blocked or inactive.'
            })

        # Ensure sender bank has sufficient balance.
        sender_bank = BankInformation.objects.select_for_update().get(
            pk=sender.bankinformation.pk,
        )
        if sender_bank.total_balance < amount.get('amount'):
            raise serializers.ValidationError({
                'amount': 'Insufficient funds.'
            })

        # Bank statement for sender.
        statement_sender = BankStatement()
        statement_sender.bank_info = sender.bankinformation
        statement_sender.sender = sender
        statement_sender.receiver = receiver_bank.holder
        statement_sender.amount = amount
        statement_sender.is_debit = True
        statement_sender.description = 'Amount transferred'
        statement_sender.save()

        # Bank statement for receiver.
        statement_receiver = BankStatement()
        statement_receiver.bank_info = receiver_bank
        statement_receiver.sender = sender
        statement_receiver.receiver = receiver_bank.holder
        statement_receiver.amount = amount
        statement_receiver.is_debit = False
        statement_receiver.description = 'Amount received'
        statement_receiver.save()

        serializer = TransactionSerializer(instance=statement_sender)
        return serializer.data


class MutationSerializer(serializers.ModelSerializer):
    sender = serializers.CharField(source='bank_info.account_number')
    status = serializers.SerializerMethodField()

    def get_status(self, obj):
        return 'Debit' if obj.is_debit else 'Credit'

    class Meta:
        model = BankStatement
        fields = [
            'id', 'created', 'amount', 'status', 'sender', 'description'
        ]
