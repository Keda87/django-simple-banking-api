from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from customers.models import Customer
from .models import BankInformation, BankStatement
from .views import BankInformationViewSet, DepositViewSet, TransferViewSet, WithdrawViewSet


class BankInformationAPITest(APITestCase):

    @classmethod
    def register_customer(cls, email, identity_id):
        user = User.objects.create_user(
            username=email,
            email=email,
            password='testing',
            first_name='tester',
            last_name='quality',
        )

        customer = Customer.objects.create(
            identity_number=identity_id,
            address='Jakarta',
            sex=Customer.MALE,
            user=user,
        )

        BankInformation.objects.create(
            account_number=BankInformation.generate_account_number(),
            holder=customer,
        )

    @classmethod
    def create_deposit(cls, bank, amount):
        deposit = BankStatement()
        deposit.bank_info = bank
        deposit.sender = bank.holder
        deposit.receiver = bank.holder
        deposit.amount = amount
        deposit.is_debit = False
        deposit.description = 'Amount deposit'
        deposit.save()

    def setUp(self):
        self.factory = APIRequestFactory()

    def test_retrieve_rekening_information(self):
        self.register_customer('tester@gmail.com', '123456')
        customer = Customer.objects.get(user__username='tester@gmail.com')

        url = reverse('v1:accounts:bankinformation-list')
        request = self.factory.get(path=url)
        force_authenticate(request, customer.user)
        view = BankInformationViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_rekening_activation_another_customer(self):
        self.register_customer('tester1@gmail.com', '123456')
        customer1 = Customer.objects.get(user__username='tester1@gmail.com')
        bank_customer1 = customer1.bankinformation

        self.register_customer('tester2@gmail.com', '123457')
        customer2 = Customer.objects.get(user__username='tester2@gmail.com')

        url = reverse('v1:accounts:bankinformation-activate', args=[bank_customer1.guid])
        request = self.factory.put(path=url)
        force_authenticate(request, customer2.user)
        view = BankInformationViewSet.as_view({'put': 'activate'})
        response = view(request, guid=bank_customer1.guid)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_rekening_activation(self):
        self.register_customer('tester@gmail.com', '123456')
        customer = Customer.objects.get(user__username='tester@gmail.com')
        bank_info = customer.bankinformation

        url = reverse('v1:accounts:bankinformation-activate', args=[bank_info.guid])
        request = self.factory.put(path=url)
        force_authenticate(request, customer.user)
        view = BankInformationViewSet.as_view({'put': 'activate'})
        response = view(request, guid=bank_info.guid)
        bank_info.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(bank_info.is_active)

    def test_block_rekening(self):
        self.register_customer('tester@gmail.com', '123456')
        customer = Customer.objects.get(user__username='tester@gmail.com')
        bank_info = customer.bankinformation
        bank_info.is_active = True
        bank_info.save()

        url = reverse('v1:accounts:bankinformation-deactivate', args=[bank_info.guid])
        request = self.factory.put(path=url)
        force_authenticate(request, customer.user)
        view = BankInformationViewSet.as_view({'put': 'deactivate'})
        response = view(request, guid=bank_info.guid)
        bank_info.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(bank_info.is_active)

    def test_unblock_rekening(self):
        self.register_customer('tester@gmail.com', '123456')
        customer = Customer.objects.get(user__username='tester@gmail.com')
        bank_info = customer.bankinformation
        bank_info.is_active = False
        bank_info.save()

        url = reverse('v1:accounts:bankinformation-activate', args=[bank_info.guid])
        request = self.factory.put(path=url)
        force_authenticate(request, customer.user)
        view = BankInformationViewSet.as_view({'put': 'activate'})
        response = view(request, guid=bank_info.guid)
        bank_info.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(bank_info.is_active)

    def test_deposit_rekening(self):
        self.register_customer('tester@gmail.com', '123456')
        customer = Customer.objects.get(user__username='tester@gmail.com')
        bank_info = customer.bankinformation
        bank_info.is_active = True
        bank_info.save()

        url = reverse('v1:accounts:deposit-list')
        data = {'amount': 20000}
        request = self.factory.post(path=url, data=data)
        force_authenticate(request, customer.user)
        view = DepositViewSet.as_view({'post': 'create'})
        response = view(request)
        bank_info.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(bank_info.total_balance, 20000)
        mutation = bank_info.mutations.first()
        self.assertEqual(mutation.description, 'Amount deposit')

    def test_deposit_inactive_rekening(self):
        self.register_customer('tester@gmail.com', '123456')
        customer = Customer.objects.get(user__username='tester@gmail.com')

        url = reverse('v1:accounts:deposit-list')
        data = {'amount': 20000}
        request = self.factory.post(path=url, data=data)
        force_authenticate(request, customer.user)
        view = DepositViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['sender'][0]), 'Bank account is blocked or inactive.')

    def test_withdraw_rekening(self):
        self.register_customer('customer1@gmail.com', '12345')
        customer = Customer.objects.get(user__email='customer1@gmail.com')
        bank_info = customer.bankinformation
        bank_info.is_active = True
        bank_info.save()
        self.create_deposit(bank_info, 100)

        data = {
            'sender': customer.pk,
            'amount': 10,
        }
        url = reverse('v1:administrations:withdraw-list')
        request = self.factory.post(path=url, data=data)
        force_authenticate(request, customer.user)
        view = WithdrawViewSet.as_view({'post': 'create'})
        response = view(request)
        bank_info.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(bank_info.total_balance, 90)
        mutation = bank_info.mutations.latest('pk')
        self.assertEqual(mutation.description, 'Amount withdrawn')

    def test_withdraw_from_inactive_rekening(self):
        self.register_customer('customer1@gmail.com', '12345')
        customer = Customer.objects.get(user__email='customer1@gmail.com')
        bank_info = customer.bankinformation
        bank_info.is_active = False
        bank_info.save()
        self.create_deposit(bank_info, 100)

        data = {
            'sender': customer.pk,
            'amount': 10,
        }
        url = reverse('v1:administrations:withdraw-list')
        request = self.factory.post(path=url, data=data)
        force_authenticate(request, customer.user)
        view = WithdrawViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['sender'][0]), 'Bank account is blocked or inactive.')

    def test_withdraw_rekening_with_amount_exceeded(self):
        self.register_customer('customer1@gmail.com', '12345')
        customer = Customer.objects.get(user__email='customer1@gmail.com')
        bank_info = customer.bankinformation
        bank_info.is_active = True
        bank_info.save()
        self.create_deposit(bank_info, 100)

        data = {
            'sender': customer.pk,
            'amount': 500,
        }
        url = reverse('v1:administrations:withdraw-list')
        request = self.factory.post(path=url, data=data)
        force_authenticate(request, customer.user)
        view = WithdrawViewSet.as_view({'post': 'create'})
        response = view(request)
        bank_info.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['amount'][0]), 'Insufficient funds.')

    def test_bank_transfer(self):
        self.register_customer('customer1@gmail.com', '12345')
        customer1 = Customer.objects.get(user__email='customer1@gmail.com')
        bank_customer1 = customer1.bankinformation
        bank_customer1.is_active = True
        bank_customer1.save()
        self.create_deposit(bank_customer1, 130000)

        self.register_customer('customer2@gmail.com', '54321')
        customer2 = Customer.objects.get(user__email='customer2@gmail.com')
        bank_customer2 = customer2.bankinformation
        bank_customer2.is_active = True
        bank_customer2.save()

        data = {
            'destination_account_number': bank_customer2.account_number,
            'amount': 30000
        }
        url = reverse('v1:administrations:transfer-list')
        request = self.factory.post(path=url, data=data)
        force_authenticate(request, customer1.user)
        view = TransferViewSet.as_view({'post': 'create'})
        response = view(request)
        bank_customer1.refresh_from_db()
        bank_customer2.refresh_from_db()
        mutation_customer1 = bank_customer1.mutations.latest('pk')
        mutation_customer2 = bank_customer2.mutations.latest('pk')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(bank_customer1.total_balance, 100000)
        self.assertEqual(bank_customer2.total_balance, 30000)
        self.assertEqual(mutation_customer1.description, 'Amount transferred')
        self.assertEqual(mutation_customer2.description, 'Amount received')

    def test_bank_transfer_with_amount_exceeded(self):
        self.register_customer('customer1@gmail.com', '12345')
        customer1 = Customer.objects.get(user__email='customer1@gmail.com')
        bank_customer1 = customer1.bankinformation
        bank_customer1.is_active = True
        bank_customer1.save()
        self.create_deposit(bank_customer1, 1000)

        self.register_customer('customer2@gmail.com', '54321')
        customer2 = Customer.objects.get(user__email='customer2@gmail.com')
        bank_customer2 = customer2.bankinformation
        bank_customer2.is_active = True
        bank_customer2.save()

        data = {
            'destination_account_number': bank_customer2.account_number,
            'amount': 5000,
        }
        url = reverse('v1:administrations:transfer-list')
        request = self.factory.post(path=url, data=data)
        force_authenticate(request, customer1.user)
        view = TransferViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['amount'][0]), 'Insufficient funds.')

    def test_bank_transfer_using_inactive_rekening(self):
        self.register_customer('customer1@gmail.com', '12345')
        customer1 = Customer.objects.get(user__email='customer1@gmail.com')
        bank_customer1 = customer1.bankinformation
        bank_customer1.is_active = False
        bank_customer1.save()
        self.create_deposit(bank_customer1, 1000)

        self.register_customer('customer2@gmail.com', '54321')
        customer2 = Customer.objects.get(user__email='customer2@gmail.com')
        bank_customer2 = customer2.bankinformation
        bank_customer2.is_active = True
        bank_customer2.save()

        data = {
            'destination_account_number': bank_customer2.account_number,
            'amount': 5000,
        }
        url = reverse('v1:administrations:transfer-list')
        request = self.factory.post(path=url, data=data)
        force_authenticate(request, customer1.user)
        view = TransferViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['sender'][0]), 'Bank account is blocked or inactive.')

    def test_bank_transfer_to_inactive_rekening(self):
        self.register_customer('customer1@gmail.com', '12345')
        customer1 = Customer.objects.get(user__email='customer1@gmail.com')
        bank_customer1 = customer1.bankinformation
        bank_customer1.is_active = True
        bank_customer1.save()
        self.create_deposit(bank_customer1, 1000)

        self.register_customer('customer2@gmail.com', '54321')
        customer2 = Customer.objects.get(user__email='customer2@gmail.com')
        bank_customer2 = customer2.bankinformation
        bank_customer2.is_active = False
        bank_customer2.save()

        data = {
            'destination_account_number': bank_customer2.account_number,
            'amount': 1000,
        }
        url = reverse('v1:administrations:transfer-list')
        request = self.factory.post(path=url, data=data)
        force_authenticate(request, customer1.user)
        view = TransferViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['receiver'][0]), 'Bank account is blocked or inactive.')

    def test_bank_transfer_to_invalid_rekening(self):
        self.register_customer('customer1@gmail.com', '12345')
        customer1 = Customer.objects.get(user__email='customer1@gmail.com')
        bank_customer1 = customer1.bankinformation
        bank_customer1.is_active = True
        bank_customer1.save()
        self.create_deposit(bank_customer1, 1000)

        self.register_customer('customer2@gmail.com', '54321')
        customer2 = Customer.objects.get(user__email='customer2@gmail.com')
        bank_customer2 = customer2.bankinformation
        bank_customer2.is_active = True
        bank_customer2.save()

        data = {
            'destination_account_number': 'HIYAHIYAHIYA',
            'amount': 1000,
        }
        url = reverse('v1:administrations:transfer-list')
        request = self.factory.post(path=url, data=data)
        force_authenticate(request, customer1.user)
        view = TransferViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['destination_account_number'][0]), 'Invalid account number.')

    def test_retrieve_rekening_mutations(self):
        self.register_customer('customer1@gmail.com', '12345')
        customer = Customer.objects.get(user__email='customer1@gmail.com')
        bank_info = customer.bankinformation
        bank_info.is_active = True
        bank_info.save()
        self.create_deposit(bank_info, 1000)

        url = reverse(
            'v1:administrations:bankinformation-mutations',
            args=[bank_info.guid.hex],
        )
        request = self.factory.get(path=url)
        force_authenticate(request, customer.user)
        view = BankInformationViewSet.as_view({'get': 'mutations'})
        response = view(request, guid=bank_info.guid)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_rekening_mutations_from_another_customer_account(self):
        self.register_customer('customer1@gmail.com', '12345')
        customer1 = Customer.objects.get(user__email='customer1@gmail.com')
        bank_customer1 = customer1.bankinformation
        bank_customer1.is_active = True
        bank_customer1.save()
        self.create_deposit(bank_customer1, 1000)

        self.register_customer('customer2@gmail.com', '54321')
        customer2 = Customer.objects.get(user__email='customer2@gmail.com')
        bank_customer2 = customer2.bankinformation
        bank_customer2.is_active = True
        bank_customer2.save()

        url = reverse(
            'v1:administrations:bankinformation-mutations',
            args=[bank_customer1.guid.hex],
        )
        request = self.factory.get(path=url)
        force_authenticate(request, customer2.user)
        view = BankInformationViewSet.as_view({'get': 'mutations'})
        response = view(request, guid=bank_customer1.guid)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
