import random
import uuid

from django.db import models

from cores.models import CommonInfo


class BankInformation(CommonInfo):
    guid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)
    account_number = models.CharField(max_length=15, unique=True)
    holder = models.OneToOneField('customers.Customer', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)

    @classmethod
    def generate_account_number(cls):
        return ''.join(random.choice('0123456789ABCDEFGH') for _ in range(13))

    def __str__(self):
        return self.account_number


class BankStatement(CommonInfo):
    bank_info = models.ForeignKey(
        BankInformation,
        related_name='mutations',
        on_delete=models.CASCADE,
    ),
    sender = models.ForeignKey(
        'customers.Customer',
        related_name='sender',
        on_delete=models.CASCADE,
    )
    receiver = models.ForeignKey(
        'customers.Customer',
        related_name='receiver',
        on_delete=models.CASCADE,
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    is_debit = models.BooleanField(default=False)

    def __str__(self):
        return self.bank_info.account_number


