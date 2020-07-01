import json

from django.test import TestCase, Client
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from secretsauce.apps.account.models import *
from secretsauce.apps.account.serializers import *
from secretsauce.apps.portal.models import *
from secretsauce.apps.portal.views import *

def reverse_args(name):
    """
    Helper function to reverse URL with arguments.
    Returns a function whose parameters are the URL arguments.
    """
    return lambda *args: reverse(name, args=tuple(args))

class CreateAccountTest(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser("admin@rms.com", "pw123123")
        self.company = Company.objects.create(
            name="McDonald's"
        )
        self.user = User.objects.create_user(
            "user1@mcdonald.com",
            "pw123123",
            company=self.company,
        )
        self.user_creation = reverse('user_creation')

    def test_user_creation(self):

        """
        Unauthorised Users cannot create new users
        """

        response = self.client.post(self.user_creation, data={
            'email': "test@gmail.com",
            'company': self.company.id
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.user_creation, data={
            'email': "test@gmail.com",
            'company': self.company.id
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        """
        Only admin Users can create new users
        """
        self.client.force_authenticate(user=self.admin)

        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.user_creation, data={
            'email': "test@gmail.com",
            'company': self.company.id
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)

        """
        Ensure email is provided
        """
        
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.user_creation, data={
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
