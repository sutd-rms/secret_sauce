from rest_framework import generics, status, permissions, mixins
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework.decorators import permission_classes

from django.core.files.storage import default_storage
from django.db.models.query import QuerySet

from secretsauce.apps.portal.models import *
from secretsauce.apps.portal.serializers import *
from secretsauce.permissions import IsOwnerOrAdmin, AdminOrReadOnly
from secretsauce.utils import UploadVerifier

class DataBlockList(generics.ListCreateAPIView):
    """
    List all datablocks or create a new datablock.

    Usage example:
        create: curl -X POST -F "name=test_file" -F "upload=@test.csv" -F "project=<uuid>" localhost:8000/datablocks/
        list: curl localhost:8000/datablocks/
    """
    queryset = DataBlock.objects.all()
    serializer_class = DataBlockSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            UploadVerifier(request.FILES['upload'])
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        assert self.queryset is not None, (
        "'%s' should either include a `queryset` attribute, "
        "or override the `get_queryset()` method."
        % self.__class__.__name__
        )

        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()

        project = self.request.query_params.get('project')
        return queryset.filter(project=project)
        
class DataBlockDetail(generics.RetrieveDestroyAPIView):
    """
    Retrieve or delete a datablock instance
    """ 

    queryset = DataBlock.objects.all()
    serializer_class = DataBlockSerializer

class ProjectList(generics.ListCreateAPIView):

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return self.queryset.all()
        return self.queryset.filter(owners=user.email)

class ProjectDetail(generics.RetrieveUpdateDestroyAPIView):

    permission_classes = [IsOwnerOrAdmin]
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

class ConstraintBlockList(generics.ListCreateAPIView):
    """
    List all constraint blocks related to a Project
    Create new constraint block
    """

    queryset = ConstraintBlock.objects.all()
    serializer_class = ConstraintBlockSerializer

    def get_queryset(self):
        assert self.queryset is not None, (
        "'%s' should either include a `queryset` attribute, "
        "or override the `get_queryset()` method."
        % self.__class__.__name__
        )

        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()

        project = self.request.query_params.get('project')
        return queryset.filter(project=project)

class ConstraintBlockDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve/Update/Destroy a ConstraintBlock
    """
    queryset = ConstraintBlock.objects.all()
    serializer_class = ConstraintBlockSerializer

class ConstraintList(generics.ListCreateAPIView):
    """
    List all constraints related to a ConstraintBlock
    Create a new constraint related to a ConstraintBlock
    """
    queryset = Constraint.objects.all()
    serializer_class = ConstraintSerializer

    def get_queryset(self):
        assert self.queryset is not None, (
        "'%s' should either include a `queryset` attribute, "
        "or override the `get_queryset()` method."
        % self.__class__.__name__
        )

        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()

        constraint_block = request.query_params.get('constraint_block')
        return queryset.filter(constraint_block=constraint_block)

class ConstraintDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve/Update/Destroy a constraint
    """
    queryset = Constraint.objects.all()
    serializer_class = ConstraintSerializer

class ConstraintParameterList(generics.ListCreateAPIView):
    """
    List all constraint parameters related to a ConstraintBlock
    """
    queryset = ConstraintParameter.objects.all()
    serializer_class = ConstraintParameterSerializer

    def get_queryset(self):
        assert self.queryset is not None, (
        "'%s' should either include a `queryset` attribute, "
        "or override the `get_queryset()` method."
        % self.__class__.__name__
        )

        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()

        constraint_block = request.query_params.get('constraint_block')
        return queryset.filter(constraint_block=constraint_block)

class ConstraintParameterDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve/Update/Destroy a constraint parameter
    """
    queryset = ConstraintParameter.objects.all()
    serializer_class = ConstraintParameterSerializer

class ConstraintRelationshipCreate(generics.CreateAPIView):
    """
    Create ConstraintParameterRelationship
    """
    queryset = ConstraintParameterRelationship.objects.all()
    serializer_class = ConstraintParameterRelationshipSerializer

class ConstraintRelationshipDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve/Update/Destroy ConstraintParameterRelationship
    """
    queryset = ConstraintParameterRelationship.objects.all()
    serializer_class = ConstraintParameterRelationshipSerializer

class PredictionModelList(generics.ListCreateAPIView):

    permission_classes = [AdminOrReadOnly]
    queryset = PredictionModel.objects.all()
    serializer_class = PredictionModelSerializer

class PredictionModelDetail(generics.RetrieveUpdateDestroyAPIView):

    permission_classes = [AdminOrReadOnly]
    queryset = PredictionModel.objects.all()
    serializer_class = PredictionModelSerializer
