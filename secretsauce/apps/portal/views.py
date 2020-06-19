from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework.decorators import permission_classes

from django.core.files.storage import default_storage

from secretsauce.apps.portal.models import *
from secretsauce.apps.portal.serializers import *
from secretsauce.permissions import IsOwnerOrAdmin, AdminOrReadOnly
from secretsauce.utils import UploadVerifier

from django.core.mail import send_mail

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

class PredictionModelList(generics.ListCreateAPIView):

    permission_classes = [AdminOrReadOnly]
    queryset = PredictionModel.objects.all()
    serializer_class = PredictionModelSerializer

class PredictionModelDetail(generics.RetrieveUpdateDestroyAPIView):

    permission_classes = [AdminOrReadOnly]
    queryset = PredictionModel.objects.all()
    serializer_class = PredictionModelSerializer
    
def email_test():
    send_mail('Subject here', 'Here is the message.', 'donotreply@rmsportal.com', ['sutdcapstone22@gmail.com'], fail_silently=False)
