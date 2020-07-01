from django.shortcuts import render
from django.core.mail import send_mail
from djoser.serializers import UserCreateSerializer

from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, mixins, generics, permissions, authentication
from rest_framework.exceptions import ErrorDetail

from djoser import signals
from djoser.compat import get_user_email
from djoser.conf import settings
from djoser.views import UserViewSet

from secretsauce.apps.account.models import *
from secretsauce.apps.account.serializers import *
from secretsauce.utils import *

class CompanyList(generics.ListCreateAPIView):

    permission_classes = [permissions.IsAdminUser]
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

class CompanyDetail(generics.RetrieveUpdateDestroyAPIView):

    permission_classes = [permissions.IsAdminUser]
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

class InviteUser(generics.CreateAPIView):

    permission_classes = [permissions.IsAdminUser]

    def create(self, request):
        # request.data.update({'password': generatePassword()})
        data = request.data.copy()
        data.update({'password': generatePassword()})
        serializer = UserCreateSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            mappings = {
            'email': serializer.data.get('email'),
            'password':  serializer.data.get('password'),
            }
            send_email('You have been invited to RMS Pricing Analytics Platform!', 'donotreply@rmsportal.com', [mappings['email']], '', 'create_user.html', mappings)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        print(serializer.errors['email'])
        if ErrorDetail(string='user with this email address already exists.', code='unique') in serializer.errors['email']:
            mappings = {
            'email': serializer.data.get('email'),
            'password':  serializer.data.get('password'),
            }
            send_email('You have been invited to RMS Pricing Analytics Platform!', 'donotreply@rmsportal.com', [mappings['email']], '', 'create_user.html', mappings)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)        
