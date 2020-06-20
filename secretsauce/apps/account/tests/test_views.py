import json

from django.test import TestCase, Client
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from secretsauce.apps.account.models import *
from secretsauce.apps.account.serializers import *
from secretsauce.apps.portal.models import *
from secretsauce.apps.portal.views import *

class UserTest(APITestCase):
    def setUp(self):
        pass

    def test_user_creation(self):
        pass
