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
        self.test_register_customer()

        payload = {
            'first_name': 'another',
            'last_name': 'adit',
            'sex': Customer.MALE,
            'identity_number': '0123456789',
            'email': 'adiyatmubarak@gmail.com',
            'password': 'testing123',
        }

        url = reverse('v1:customers:customer-list')
        request = self.factory.post(path=url, data=payload)
        view = CustomerViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {
            'username': ['This username is already taken.'],
        })


class CustomerAuthAPITest(APITestCase):

    def setUp(self):
        pass