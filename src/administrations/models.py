import random
import uuid

from django.db import models
from django.db.models import Sum

from cores.models import CommonInfo


class BankInformation(CommonInfo):
    guid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)
    account_number = models.CharField(max_length=15, unique=True)
    holder = models.OneToOneField('customers.Customer', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)

    @property
    def total_balance(self):
        aggregate_credit = BankStatement.objects.filter(
            bank_info__pk=self.pk,
            is_debit=False,
        ).aggregate(total=Sum('amount'))

        aggregate_debit = BankStatement.objects.filter(
            bank_info__pk=self.pk,
            is_debit=True,
        ).aggregate(total=Sum('amount'))

        credit = aggregate_credit.get('total')
        credit = credit if credit is not None else 0

        debit = aggregate_debit.get('total')
        debit = debit if debit is not None else 0

        return credit - debit

    @classmethod
    def generate_account_number(cls):
        return ''.join(random.choice('0123456789ABCDEFGH') for _ in range(13))

    def __str__(self):
        return self.account_number


class BankStatement(CommonInfo):
    bank_info = models.ForeignKey(  # Bank information for the receiver.
        BankInformation,
        related_name='mutations',
        on_delete=models.CASCADE,
    )
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
    description = models.TextField()

    def __str__(self):
        return (f'Owner: {self.bank_info.holder.user.get_full_name()} '
                f'{"Debit: " if self.is_debit else "Credit: "} {self.amount}')


