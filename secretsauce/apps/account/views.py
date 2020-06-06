from django.shortcuts import render
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
