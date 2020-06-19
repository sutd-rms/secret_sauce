from django.shortcuts import render
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, mixins, generics, permissions, authentication

from djoser import signals
from djoser.compat import get_user_email
from djoser.conf import settings
from djoser.views import UserViewSet

from secretsauce.apps.account.models import Invitation, Company
from secretsauce.apps.account.serializers import InvitationSerializer, CompanySerializer

class InvitationCreator(mixins.CreateModelMixin,
                        mixins.ListModelMixin,
                        generics.GenericAPIView):
    """
    Create a new invitation
    """

    permission_classes = [permissions.IsAdminUser]
    queryset = Invitation.objects.all()
    serializer_class = InvitationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            email = serializer.data.get('email')
            invitation_id = serializer.data.get('id')
            message = "Your invitation code is " + invitation_id + "."
            send_mail('Invitation to the RMS Club', message, 'sutdcapstone22@gmail.com', [email], fail_silently=False)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif 'invitation with this email already exists.' in serializer.errors['email']:
            email = serializer.data.get('email')
            invitation_id = str(Invitation.objects.get(email=email).id)
            message = "Your invitation code is " + invitation_id + "."
            send_mail('Invitation to the RMS Club', message, 'sutdcapstone22@gmail.com', [email], fail_silently=False)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class InvitationDetail(mixins.RetrieveModelMixin,
                       generics.GenericAPIView):
    """
    Check invitation validity
    """

    queryset = Invitation.objects.all()
    serializer_class = InvitationSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

class CompanyList(generics.ListCreateAPIView):

    permission_classes = [permissions.IsAdminUser]
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

class CompanyDetail(generics.RetrieveUpdateDestroyAPIView):

    permission_classes = [permissions.IsAdminUser]
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
