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

from secretsauce.apps.account.models import Invitation
from secretsauce.apps.account.serializers import InvitationSerializer

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
            print(send_mail('Invitation to the RMS Club', message, 'sutdcapstone22@gmail.com', [email], fail_silently=False))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
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
