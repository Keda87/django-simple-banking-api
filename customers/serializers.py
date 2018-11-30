from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import serializers

from administrations.models import BankInformation
from customers.models import Customer


class SimpleUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
        ]


class CustomerSignUpSerializer(serializers.Serializer):
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        if User.objects.filter(username=email).exists():
            raise serializers.ValidationError({
                'username': 'This username is already taken.'
            })
        return attrs


class CustomerSerializer(CustomerSignUpSerializer,
                         serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)

    @transaction.atomic
    def create(self, validated_data):
        email = validated_data.get('email')

        user = User.objects.create_user(
            username=email,
            email=email,
            password=validated_data.get('password'),
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
        )

        customer = Customer.objects.create(
            identity_number=validated_data.get('identity_number'),
            address=validated_data.get('address'),
            sex=validated_data.get('sex'),
            user=user,
        )

        BankInformation.objects.create(
            account_number=BankInformation.generate_account_number(),
            holder=customer,
        )

        return customer

    class Meta:
        model = Customer
        fields = [
            'id', 'guid', 'address', 'sex', 'identity_number', 'user',
            'first_name', 'last_name', 'email', 'password',
        ]
        read_only_fields = ['id', 'guid']
