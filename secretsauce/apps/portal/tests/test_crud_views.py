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

class ProjectCRUDTest(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser("admin@rms.com", "pw123123")
        self.company = Company.objects.create(
            name="McDonald's"
        )
        self.user = User.objects.create_user(
            "user1@mcdonald.com",
            "pw123123",
            invitation=Invitation.objects.create(email="user1@mcdonald.com"),
            company=self.company,
        )

        self.p1 = Project.objects.create(
            title="Admin Project",
            company=self.company
        )
        self.p1.owners.add(self.admin)

        self.p2 = Project.objects.create(
            title="User Project",
            company=self.company
        )
        self.p2.owners.add(self.user)

        self.list_url = reverse('project-list')
        self.detail_url = reverse_args('project-detail')

    def test_list(self):
        """
        Test the List function for Project views
        """
        # Admin can see all Projects
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        # User can only see
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.list_url, data={
            'title': "My new project",
            'company': self.company.id,
            'owners': [self.admin.email],
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.list_url, data={
            'title': "My other new project",
            'company': self.company.id,
            'owners': [self.user.email],
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve(self):
        # Admin can retrieve any project
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.detail_url(self.p1.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('id'), str(self.p1.id))

        response = self.client.get(self.detail_url(self.p2.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('id'), str(self.p2.id))

        # User can only retrieve their projects
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.detail_url(self.p1.id))
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(self.detail_url(self.p2.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('id'), str(self.p2.id))

    def test_update(self):
        pass

    def test_partial_update(self):
        pass

    def test_destroy(self):
        pass

class PredictionModelCRUDTest(APITestCase):
    def setUp(self):
        pass

    def test_list(self):
        pass

    def test_create(self):
        pass

    def test_retrieve(self):
        pass

    def test_update(self):
        pass

    def test_partial_update(self):
        pass

    def test_destroy(self):
        pass

class ModelTagCRUDTest(APITestCase):
    def setUp(self):
        pass

    def test_list(self):
        pass

    def test_create(self):
        pass

    def test_retrieve(self):
        pass

    def test_update(self):
        pass

    def test_partial_update(self):
        pass

    def test_destroy(self):
        pass

class DataBlockCRUDTest(APITestCase):
    def setUp(self):
        pass

    def test_list(self):
        pass

    def test_create(self):
        pass

    def test_retrieve(self):
        pass

    def test_update(self):
        pass

    def test_partial_update(self):
        pass

    def test_destroy(self):
        pass

class ConstraintBlockCRUDTest(APITestCase):
    def setUp(self):
        pass

    def test_list(self):
        pass

    def test_create(self):
        pass

    def test_retrieve(self):
        pass

    def test_update(self):
        pass

    def test_partial_update(self):
        pass

    def test_destroy(self):
        pass

class ConstraintCRUDTest(APITestCase):
    def setUp(self):
        pass

    def test_list(self):
        pass

    def test_create(self):
        pass

    def test_retrieve(self):
        pass

    def test_update(self):
        pass

    def test_partial_update(self):
        pass

    def test_destroy(self):
        pass

class ConstraintParameterCRUDTest(APITestCase):
    def setUp(self):
        pass

    def test_list(self):
        pass

    def test_create(self):
        pass

    def test_retrieve(self):
        pass

    def test_update(self):
        pass

    def test_partial_update(self):
        pass

    def test_destroy(self):
        pass

class ConstraintParameterRelationshipCRUDTest(APITestCase):
    def setUp(self):
        pass

    def test_list(self):
        pass

    def test_create(self):
        pass

    def test_retrieve(self):
        pass

    def test_update(self):
        pass

    def test_partial_update(self):
        pass

    def test_destroy(self):
        pass
