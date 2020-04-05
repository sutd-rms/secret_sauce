from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import generics, permissions
from rest_framework.response import Response
from knox.models import AuthToken

from secretsauce.apps.account.models import MyUser
from secretsauce.apps.account.serializer import RegisterSerializer, UserSerializer, LoginSerializer, MyUserSerializer


# Register API
class RegisterAPI(generics.CreateAPIView):
  serializer_class = MyUserSerializer
  permission_classes = (permissions.AllowAny,)
  queryset = MyUser.objects.all()

  @transaction.atomic
  def post(self, request, *args, **kwargs):
    serializer = MyUserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    authuser = User.objects.create_user(username=request.data['username'], email=request.data['email'])
    return Response({
      "user": MyUserSerializer(user, context=self.get_serializer_context()).data,
      "token": AuthToken.objects.create(authuser)[1]
    })

# Login API
class LoginAPI(generics.GenericAPIView):
  serializer_class = LoginSerializer

  def post(self, request, *args, **kwargs):
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data
    # authuser = User.objects.create_user(username=request.data['username'])
    return Response({
      "user": MyUserSerializer(user, context=self.get_serializer_context()).data,
      "token": AuthToken.objects.create(user)[1]
    })

# Get User API
class UserAPI(generics.RetrieveAPIView):
  permission_classes = [
    permissions.IsAuthenticated,
  ]
  serializer_class = UserSerializer

  def get_object(self):
    return self.request.user