from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIRequestFactory

from customers.views import CustomerViewSet
from .models import Customer


class CustomerAPITest(APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()

    def test_register_customer(self):
        payload = {
            'first_name': 'adiyat',
            'last_name': 'mubarak',
            'address': 'JL Dorowati barat 33',
            'sex': Customer.MALE,
            'identity_number': '0123456789',
            'email': 'adiyatmubarak@gmail.com',
            'password': 'testing123',
        }

        url = reverse('v1:customers:customer-list')
        request = self.factory.post(path=url, data=payload)
        view = CustomerViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_customer_with_email_taken(self):
        user = User.objects.create_user(
            username='tester@simplebank.com',
            email='tester@simplebank.com',
            password='testing123',
            first_name='qa',
            last_name='engineer',
        )
        Customer.objects.create(
            identity_number='1234',
            address='Jauh alamat',
            sex=Customer.MALE,
            user=user,
        )

        payload = {
            'first_name': 'another',
            'last_name': 'adit',
            'sex': Customer.MALE,
            'identity_number': '0123456789',
            'email': 'tester@simplebank.com',
            'password': 'testing123',
            'address': 'alamat jauh sekali',
        }

        url = reverse('v1:customers:customer-list')
        request = self.factory.post(path=url, data=payload)
        view = CustomerViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {
            'username': ['This username is already taken.'],
        })
