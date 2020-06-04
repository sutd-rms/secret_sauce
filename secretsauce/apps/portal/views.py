from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser

from django.core.files.storage import default_storage

from secretsauce.apps.portal.models import *
from secretsauce.apps.portal.serializers import *

from .utils import UploadVerifier
from django.core.mail import send_mail

class DataBlockList(generics.ListCreateAPIView):
    """
    List all datablocks or create a new datablock.

    Usage example:
        create: curl -X POST -F "name=test_file" -F "upload=@test.csv" localhost:8000/datablocks/
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

def email_test():
    send_mail('Subject here', 'Here is the message.', 'donotreply@rmsportal.com', ['sutdcapstone22@gmail.com'], fail_silently=False)
