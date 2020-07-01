import json

from django.test import TestCase, Client
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from secretsauce.utils import reverse_args
from secretsauce.apps.account.models import *
from secretsauce.apps.account.serializers import *
from secretsauce.apps.portal.models import *
from secretsauce.apps.portal.views import *

class ProjectCRUDTest(APITestCase):
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
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.get(self.detail_url(self.p2.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('id'), str(self.p2.id))

    def test_update(self):

        # Admin update any project
        self.client.force_authenticate(user=self.admin)
        response = self.client.put(self.detail_url(self.p1.id), data={
            'title': "New name",
            'company': self.company.id,
            'owners': [self.admin.email],
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('title'), "New name")

        response = self.client.put(self.detail_url(self.p2.id), data={
            'title': "New name 2",
            'company': self.company.id,
            'owners': [self.user.email],
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('title'), "New name 2")

        # User 
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.detail_url(self.p1.id), data={
            'title': "New name 2",
            'company': self.company.id,
            'owners': [self.admin.email],
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.put(self.detail_url(self.p2.id), data={
            'title': "New name 2",
            'company': self.company.id,
            'owners': [self.user.email],
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('title'), "New name 2")

    def test_partial_update(self):
        # Admin update any project
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(self.detail_url(self.p1.id), data={
            'title': "New name",
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('title'), "New name")

        response = self.client.patch(self.detail_url(self.p2.id), data={
            'title': "New name 2",
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('title'), "New name 2")

        # User 
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.detail_url(self.p1.id), data={
            'title': "New name 3",
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.patch(self.detail_url(self.p2.id), data={
            'title': "New name 4",
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('title'), "New name 4")

    def test_destroy(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.detail_url(self.p1.id))
        response = self.client.delete(self.detail_url(self.p2.id))
        self.assertEqual(len(Project.objects.all()), 1)

        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(self.detail_url(self.p1.id))
        self.assertEqual(len(Project.objects.all()), 0)


class PredictionModelCRUDTest(APITestCase):
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
        self.pred_model = PredictionModel.objects.create(name='XGBoost')
        self.list_url = reverse('prediction-model-list')
        self.detail_url = reverse_args('prediction-model-detail')

    def test_list(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.list_url, data={
            'name': "Neural Network"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(PredictionModel.objects.all()), 2)

        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.list_url, data={
            'name': "Another model"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(len(PredictionModel.objects.all()), 2)

    def test_retrieve(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.detail_url(self.pred_model.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.detail_url(self.pred_model.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.put(self.detail_url(self.pred_model.id), data={
            'name': "NN",
            'description': ""
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('name'), "NN")

        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.detail_url(self.pred_model.id), data={
            'name': "NN2",
            'description': ""
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_partial_update(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(self.detail_url(self.pred_model.id), data={
            'description': "This is a neural network"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('description'), "This is a neural network")

        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.detail_url(self.pred_model.id), data={
            'description': "This is a neural network 2"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_destroy(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.detail_url(self.pred_model.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(self.detail_url(self.pred_model.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(PredictionModel.objects.all()), 0)

class ModelTagCRUDTest(APITestCase):
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

        self.pred_model1 = PredictionModel.objects.create(name="Attention Neural Net")
        self.pred_model2 = PredictionModel.objects.create(name="Gradient Boosted Decision Tree")

        self.model_tag = ModelTag.objects.create(name="Neural Network")
        self.model_tag.models.add(self.pred_model1)

        self.list_url = reverse('model-tag-list')
        self.detail_url = reverse_args('model-tag-detail')

    def test_list(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.list_url, data={
            'name': "Decision Tree",
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(ModelTag.objects.all()), 2)

        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.list_url, data={
            'name': "New Tag"
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.detail_url(self.model_tag.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.put(self.detail_url(self.model_tag.pk), data={
            'name': "Neural Network!!!",
            'description': "These are neural networks",
            'models': [model.id for model in self.model_tag.models.all()]
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.detail_url(self.model_tag.pk), data={
            'name': "Neural Network!!!",
            'description': "These are neural networks!!",
            'models': self.model_tag.models
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_partial_update(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(self.detail_url(self.model_tag.pk), data={
            'description': "These are neural networks",
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.detail_url(self.model_tag.pk), data={
            'description': "These are neural networks!!",
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_destroy(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.detail_url(self.model_tag.pk))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(self.detail_url(self.model_tag.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(ModelTag.objects.all()), 0)

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
        self.admin = User.objects.create_superuser("admin@rms.com", "pw123123")
        self.company = Company.objects.create(
            name="McDonald's"
        )
        self.user = User.objects.create_user(
            "user1@mcdonald.com",
            "pw123123",
            company=self.company,
        )

        self.project = Project.objects.create(title="First project", company=self.company)
        self.project.owners.add(self.user)
        self.constraint_block = ConstraintBlock.objects.create(name="Block 1", project=self.project)

        self.list_url = reverse('constraint-block-list')
        self.detail_url = reverse_args('constraint-block-detail')

    def test_list(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.list_url, data={
            'project': self.project.id
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, data={
            'project': self.project.id
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.list_url, data={
            'name': "Block 2",
            'project': self.project.id,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(ConstraintBlock.objects.all()), 2)

        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.list_url, data={
            'name': "Block 3",
            'project': self.project.id,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(ConstraintBlock.objects.all()), 3)

    def test_retrieve(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.detail_url(self.constraint_block.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.detail_url(self.constraint_block.id), data={
            'name': "New name",
            'project': self.project.id
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('name'), "New name")

    def test_partial_update(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.detail_url(self.constraint_block.id), data={
            'name': "New name",
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('name'), "New name")

    def test_destroy(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.detail_url(self.constraint_block.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(ConstraintBlock.objects.all()), 0)

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
