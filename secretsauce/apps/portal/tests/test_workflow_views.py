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

class ProjectTests(APITestCase):
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
        self.project_data = {
            'title': "My first project",
            'company': self.company.id,
            'owners': [self.admin.email],
        }
        self.list_url = reverse('project-list')
        self.detail_url = reverse_args('project-detail')

    def test_create_project(self):
        """
        Test project creation
        """
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.list_url, data=self.project_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_project_list(self):
        """
        Test for retrieving project list
        """
        
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.list_url, data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

        # Create new project
        response = self.client.post(self.list_url, data=self.project_data, format='json')

        response = self.client.get(self.list_url, data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


    def test_get_project_detail(self):
        """
        Test retrieving project details
        """

        self.client.force_authenticate(user=self.admin)

        # Create new project
        response = self.client.post(self.list_url, data=self.project_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # List projects
        response = self.client.get(self.list_url, data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        project_id = response.data[0].get('id')

        # Get project
        response = self.client.get(self.detail_url(project_id), data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('title'), self.project_data['title'])

    def test_add_owner(self):
        """
        Test to update the owners in a project
        """

        # Create new project
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.list_url, data=self.project_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        project_id = response.data.get('id')

        # Attempt to access project with user account
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
        response = self.client.get(self.detail_url(project_id), data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Add user as owner
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(self.detail_url(project_id), data={
            'owners': [self.admin.email, self.user.email]
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Attempt to access project with user account
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        response = self.client.get(self.detail_url(project_id), data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('id'), project_id)

class DataBlockTests(APITestCase):
    pass

class ConstraintTests(APITestCase):
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
        self.project = Project.objects.create(
            title='My first project',
            company=self.company,
        )
        self.project.owners.add(self.admin)

        self.first_cb = ConstraintBlock.objects.create(
            project=self.project,
            name="First Constraint Block"
        )

        self.list_url = reverse('constraint-block-list')
        self.detail_url = reverse_args('constraint-block-detail')
        self.constraint_list_url = reverse('constraint-list')
        self.constraint_detail_url = reverse_args('constraint-detail')
        self.param_list_url = reverse('constraint-parameter-list')
        self.param_detail_url = reverse_args('constraint-parameter-detail')
        self.rel_create_url = reverse('constraint-relationship-create')
        self.rel_detail_url = reverse_args('constraint-relationship-detail')

    def test_get_constraint_block_list(self):
        """
        Test retrieving list of ConstraintBlocks related to a project
        """
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.list_url, data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
        response = self.client.get(self.list_url, data={'project':self.project.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_constraint_block(self):
        """
        Test creation of ConstraintBlock
        """
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.list_url, data={
            'project': self.project.id,
            'name': "Second Constraint Block"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get('name'), "Second Constraint Block")

    # def test_get_constraint_block_detail(self):
    #     pass

    def test_add_constraint_equation(self):
        self.client.force_authenticate(user=self.admin)

        # New constraint parameters
        response = self.client.post(self.param_list_url, data={
            'name': "Big Mac Price",
            'constraint_block': self.first_cb.id
        }, format='json')   
        bmac = response.data.get('id')
        response = self.client.post(self.param_list_url, data={
            'name': "Cheeseburger Price",
            'constraint_block': self.first_cb.id
        }, format='json')  
        cburger = response.data.get('id')

        # New constraint
        response = self.client.post(self.constraint_list_url, data={
            'constraint_block': self.first_cb.id,
            'name': "Big Mac more expensive than Cheeseburger",
            'in_equality': "GEQ"
        }, format='json')    
        c = response.data.get('id')

        # New constraint relationships
        response = self.client.post(self.rel_create_url, data={
            'constraint': c,
            'constraint_parameter': bmac,
            'coefficient': '+1'
        }, format='json')
        response = self.client.post(self.rel_create_url, data={
            'constraint': c,
            'constraint_parameter': cburger,
            'coefficient': '-1'
        })

        # Check constraint
        response = self.client.get(self.constraint_detail_url(c))

        response = self.client.get(self.list_url, data={'project': self.project.id})

    # def test_add_constraint(self):
    #     pass

class PredictionModelTests(APITestCase):
    pass
