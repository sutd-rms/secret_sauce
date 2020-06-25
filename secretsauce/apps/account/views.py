from django.shortcuts import render
from django.core.mail import send_mail
from djoser.serializers import UserCreateSerializer
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, mixins, generics, permissions, authentication
import random
import string

from djoser import signals
from djoser.compat import get_user_email
from djoser.conf import settings
from djoser.views import UserViewSet

from secretsauce.apps.account.models import *
from secretsauce.apps.account.serializers import *


def generatePassword(stringLength=10):
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join((random.choice(lettersAndDigits) for i in range(stringLength)))
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
        password = generatePassword()
        user = User.objects.create_user(
            request.data['email'],
            password
        )
        user.save()
        serializer=UserCreateSerializer(user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
        # send_mail('Subject here', 'Here is the message.', 'donotreply@rmsportal.com', ['sutdcapstone22@gmail.com'], fail_silently=False)

