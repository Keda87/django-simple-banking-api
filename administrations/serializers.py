from rest_framework import serializers

from administrations.models import BankInformation


class AccountSerializer(serializers.ModelSerializer):
    holder = serializers.CharField(source='holder.user.get_full_name')

    class Meta:
        model = BankInformation
        fields = [
            'id', 'guid', 'account_number', 'holder', 'is_active',
        ]